r"""
Matrix Spaces.

You can create any space `\text{Mat}_{n\times m}(R)` of
either dense or sparse matrices with given number of rows and
columns over any commutative or noncommutative ring.

EXAMPLES::

    sage: MS = MatrixSpace(QQ,6,6,sparse=True); MS
    Full MatrixSpace of 6 by 6 sparse matrices over Rational Field
    sage: MS.base_ring()
    Rational Field
    sage: MS = MatrixSpace(ZZ,3,5,sparse=False); MS
    Full MatrixSpace of 3 by 5 dense matrices over Integer Ring

TESTS::

    sage: matrix(RR,2,2,sparse=True)
    [0.000000000000000 0.000000000000000]
    [0.000000000000000 0.000000000000000]
    sage: matrix(GF(11),2,2,sparse=True)
    [0 0]
    [0 0]
"""

# System imports
import types
import weakref
import operator

# Sage matrix imports
import matrix
import matrix_generic_dense
import matrix_generic_sparse

import matrix_modn_dense
import matrix_modn_sparse

import matrix_mod2_dense
#import matrix_mod2_sparse

import matrix_integer_dense
import matrix_integer_sparse

import matrix_rational_dense
import matrix_rational_sparse

import matrix_mpolynomial_dense

#import padics.matrix_padic_capped_relative_dense

## import matrix_cyclo_dense
## import matrix_cyclo_sparse


# IMPORTANT - these two guys get imported below only later
# since they currently force numpy to import, which takes
# a *long* time. 
#import matrix_real_double_dense
#import matrix_complex_double_dense

import sage.groups.matrix_gps.matrix_group_element


# Sage imports
import sage.structure.coerce
import sage.structure.parent_gens as parent_gens
import sage.rings.ring as ring
import sage.rings.rational_field as rational_field
import sage.rings.integer_ring as integer_ring
import sage.rings.integer as integer
import sage.rings.field as field
import sage.rings.principal_ideal_domain as principal_ideal_domain
import sage.rings.integral_domain as integral_domain
import sage.rings.number_field.all
import sage.rings.finite_rings.integer_mod_ring
import sage.rings.polynomial.multi_polynomial_ring_generic
import sage.misc.latex as latex
#import sage.rings.real_double as real_double
import sage.misc.mrange
import sage.modules.free_module_element
import sage.modules.free_module
from sage.structure.sequence import Sequence

from sage.categories.rings import Rings

def is_MatrixSpace(x):
    """
    Returns True if self is an instance of MatrixSpace returns false if
    self is not an instance of MatrixSpace
    
    EXAMPLES::
    
        sage: from sage.matrix.matrix_space import is_MatrixSpace
        sage: MS = MatrixSpace(QQ,2)
        sage: A = MS.random_element()
        sage: is_MatrixSpace(MS)
        True
        sage: is_MatrixSpace(A)
        False
        sage: is_MatrixSpace(5)
        False
    """

    return isinstance(x, MatrixSpace_generic)

_cache = {}
def MatrixSpace(base_ring, nrows, ncols=None, sparse=False):
    """
    Create with the command
    
    MatrixSpace(base_ring , nrows [, ncols] [, sparse])
    
    The default value of the optional argument sparse is False. The
    default value of the optional argument ncols is nrows.
    
    INPUT:
    
    
    -  ``base_ring`` - a ring
    
    -  ``nrows`` - int, the number of rows
    
    -  ``ncols`` - (default nrows) int, the number of
       columns
    
    -  ``sparse`` - (default false) whether or not matrices
       are given a sparse representation
    
    
    OUTPUT: The unique space of all nrows x ncols matrices over
    base_ring.
    
    EXAMPLES::
    
        sage: MS = MatrixSpace(RationalField(),2)
        sage: MS.base_ring()
        Rational Field
        sage: MS.dimension()
        4
        sage: MS.dims()
        (2, 2)
        sage: B = MS.basis()
        sage: B
        [
        [1 0]  [0 1]  [0 0]  [0 0]
        [0 0], [0 0], [1 0], [0 1]
        ]
        sage: B[0]
        [1 0]
        [0 0]
        sage: B[1]
        [0 1]
        [0 0]
        sage: B[2]
        [0 0]
        [1 0]
        sage: B[3]
        [0 0]
        [0 1]
        sage: A = MS.matrix([1,2,3,4])
        sage: A
        [1 2]
        [3 4]
        sage: MS2 = MatrixSpace(RationalField(),2,3)
        sage: B = MS2.matrix([1,2,3,4,5,6])
        sage: A*B
        [ 9 12 15]
        [19 26 33]
    
    ::
    
        sage: M = MatrixSpace(ZZ, 10)
        sage: M
        Full MatrixSpace of 10 by 10 dense matrices over Integer Ring
        sage: loads(M.dumps()) == M
        True
    """
    if not base_ring in Rings():
        raise TypeError("base_ring (=%s) must be a ring"%base_ring)
    
    if ncols is None: ncols = nrows
    nrows = int(nrows); ncols = int(ncols); sparse=bool(sparse)
    key = (base_ring, nrows, ncols, sparse)
    if _cache.has_key(key):
        M = _cache[key]()
        if not M is None: return M

    M = MatrixSpace_generic(base_ring, nrows, ncols, sparse)

    _cache[key] = weakref.ref(M)
    return M


    
class MatrixSpace_generic(parent_gens.ParentWithGens):
    """
    The space of all nrows x ncols matrices over base_ring.
    
    EXAMPLES::
    
        sage: MatrixSpace(ZZ,10,5)
        Full MatrixSpace of 10 by 5 dense matrices over Integer Ring
        sage: MatrixSpace(ZZ,10,5).category()
        Category of modules over Integer Ring

        sage: MatrixSpace(ZZ,10,2^31)
        Traceback (most recent call last):                                   # 32-bit
        ...                                                                  # 32-bit
        ValueError: number of rows and columns must be less than 2^31 (on a 32-bit computer -- use a 64-bit computer for matrices with up to 2^63-1 rows and columns)           # 32-bit
        Full MatrixSpace of 10 by 2147483648 dense matrices over Integer Ring   # 64-bit
        sage: MatrixSpace(ZZ,2^31,10)
        Traceback (most recent call last):                                   # 32-bit
        ...                                                                  # 32-bit
        ValueError: number of rows and columns must be less than 2^31 (on a 32-bit computer -- use a 64-bit computer for matrices with up to 2^63-1 rows and columns)           # 32-bit
        Full MatrixSpace of 2147483648 by 10 dense matrices over Integer Ring   # 64-bit
        sage: MatrixSpace(ZZ,10,10).category()
        Category of algebras over Integer Ring
        sage: MatrixSpace(QQ,10).category()
        Category of algebras over Rational Field
    """

    def __init__(self,  base_ring,             
                        nrows, 
                        ncols=None, 
                        sparse=False):

        if ncols == None: ncols = nrows
        from sage.categories.all import Modules, Algebras
        parent_gens.ParentWithGens.__init__(self, base_ring) # category = Modules(base_ring)
        # Temporary until the inheritance glitches are fixed
        category = Algebras(base_ring) if nrows == ncols else Modules(base_ring)
        sage.structure.category_object.CategoryObject._init_category_(self, category)

        if not base_ring in Rings():
            raise TypeError("base_ring must be a ring")
        nrows = int(nrows)
        ncols = int(ncols)
        if nrows < 0:
            raise ArithmeticError("nrows must be nonnegative")
        if ncols < 0:
            raise ArithmeticError("ncols must be nonnegative")

        if nrows >= 2**63 or ncols >= 2**63:
            raise ValueError("number of rows and columns must be less than 2^63")
        elif (nrows >= 2**31 or ncols >= 2**31) and not sage.misc.misc.is_64_bit:
            raise ValueError("number of rows and columns must be less than 2^31 (on a 32-bit computer -- use a 64-bit computer for matrices with up to 2^63-1 rows and columns)")
            
        self.__nrows = nrows
        self.__is_sparse = sparse
        if ncols == None:
            self.__ncols = nrows
        else:
            self.__ncols = ncols
        self.__matrix_class = self._get_matrix_class()

    def __reduce__(self):
        """
        EXAMPLES::
        
            sage: A = Mat(ZZ,5,7,sparse=True)
            sage: A
            Full MatrixSpace of 5 by 7 sparse matrices over Integer Ring
            sage: loads(dumps(A)) == A
            True
        """
        return MatrixSpace, (self.base_ring(), self.__nrows, self.__ncols, self.__is_sparse)

    def __call__(self, entries=0, coerce=True, copy=True, rows=None):
        """
        EXAMPLES::
        
            sage: k = GF(7); G = MatrixGroup([matrix(k,2,[1,1,0,1]), matrix(k,2,[1,0,0,2])])
            sage: g = G.0
            sage: MatrixSpace(k,2)(g)
            [1 1]
            [0 1]
        
        ::
        
            sage: MS = MatrixSpace(ZZ,2,4)
            sage: M2 = MS(range(8)); M2
            [0 1 2 3]
            [4 5 6 7]
            sage: M2.columns()
            [(0, 4), (1, 5), (2, 6), (3, 7)]
            sage: MS(M2.columns())
            [0 1 2 3]
            [4 5 6 7]
            sage: M2 == MS(M2.columns())
            True
            sage: M2 == MS(M2.rows())
            True
        
        ::
        
            sage: MS = MatrixSpace(ZZ,2,4, sparse=True)
            sage: M2 = MS(range(8)); M2
            [0 1 2 3]
            [4 5 6 7]
            sage: M2.columns()
            [(0, 4), (1, 5), (2, 6), (3, 7)]
            sage: MS(M2.columns())
            [0 1 2 3]
            [4 5 6 7]
            sage: M2 == MS(M2.columns())
            True
            sage: M2 == MS(M2.rows())
            True
        
        ::
        
            sage: MS = MatrixSpace(ZZ,2,2)
            sage: MS([1,2,3,4])
            [1 2]
            [3 4]
            sage: MS([1,2,3,4], rows=True)
            [1 2]
            [3 4]
            sage: MS([1,2,3,4], rows=False)
            [1 3]
            [2 4]
        
        ::
        
            sage: MS = MatrixSpace(ZZ,2,2, sparse=True)
            sage: MS([1,2,3,4])
            [1 2]
            [3 4]
            sage: MS([1,2,3,4], rows=True)
            [1 2]
            [3 4]
            sage: MS([1,2,3,4], rows=False)
            [1 3]
            [2 4]

            sage: MS = MatrixSpace(ZZ, 2)
            sage: g = Gamma0(5)([1,1,0,1])
            sage: MS(g)
            [1 1]
            [0 1]

        ::

            sage: MS = MatrixSpace(ZZ,2,2, sparse=True)
            sage: mat = MS(); mat
            [0 0]
            [0 0]
            sage: mat.is_mutable()
            True
            sage: mat2 = mat.change_ring(QQ); mat2.is_mutable()
            True
        """
        if entries is None or entries == 0:
            if self.__is_sparse: # faster to create a new one than copy.
                return self.__matrix_class(self, {}, coerce=coerce, copy=copy)
            else:
                return self.zero_matrix().__copy__()

        if isinstance(entries, (list, tuple)) and len(entries) > 0 and \
           sage.modules.free_module_element.is_FreeModuleElement(entries[0]):
            #Try to determine whether or not the entries should
            #be rows or columns
            if rows is None:
                #If the matrix is square, default to rows
                if self.__ncols == self.__nrows:
                    rows = True
                elif len(entries[0]) == self.__ncols:
                    rows = True
                elif len(entries[0]) == self.__nrows:
                    rows = False
                else:
                    raise ValueError("incorrect dimensions")
            
            if self.__is_sparse:
                e = {}
                zero = self.base_ring()(0)
                for i in xrange(len(entries)):
                    for j, x in entries[i].iteritems():
                        if x != zero:
                            if rows:
                                e[(i,j)] = x
                            else:
                                e[(j,i)] = x
                entries = e
            else:
                entries = sum([v.list() for v in entries],[])

        if rows is None:
            rows = True

        if not self.__is_sparse and isinstance(entries, dict):
            entries = dict_to_list(entries, self.__nrows, self.__ncols)
            coerce = True
            copy = False
        elif self.__is_sparse and isinstance(entries, (list, tuple)):
            entries = list_to_dict(entries, self.__nrows, self.__ncols, rows=rows)
            coerce = True
            copy = False
        elif sage.groups.matrix_gps.matrix_group_element.is_MatrixGroupElement(entries) \
             or isinstance(entries, sage.modular.arithgroup.arithgroup_element.ArithmeticSubgroupElement):
            return self(entries.matrix(), copy=False)

        return self.matrix(entries, copy=copy, coerce=coerce, rows=rows)

    def change_ring(self, R):
        """
        Return matrix space over R with otherwise same parameters as self.
        
        INPUT:
        
        
        -  ``R`` - ring
        
        
        OUTPUT: a matrix space
        
        EXAMPLES::
        
            sage: Mat(QQ,3,5).change_ring(GF(7))
            Full MatrixSpace of 3 by 5 dense matrices over Finite Field of size 7
        """
        try:
            return self.__change_ring[R]
        except AttributeError:
            self.__change_ring = {}
        except KeyError:
            pass
        M = MatrixSpace(R, self.__nrows, self.__ncols, self.__is_sparse)
        self.__change_ring[R] = M
        return M

    def base_extend(self, R):
        """
        Return base extension of this matrix space to R.
        
        INPUT:

        -  ``R`` - ring

        OUTPUT: a matrix space
        
        EXAMPLES::
        
            sage: Mat(ZZ,3,5).base_extend(QQ)
            Full MatrixSpace of 3 by 5 dense matrices over Rational Field
            sage: Mat(QQ,3,5).base_extend(GF(7))
            Traceback (most recent call last):
            ...
            TypeError: no base extension defined
        """
        if R.has_coerce_map_from(self.base_ring()):
            return self.change_ring(R)
        raise TypeError("no base extension defined")
        
    def construction(self):
        """
        EXAMPLES::
        
            sage: A = matrix(ZZ, 2, [1..4], sparse=True)
            sage: A.parent().construction()
            (MatrixFunctor, Integer Ring)
            sage: A.parent().construction()[0](QQ['x'])
            Full MatrixSpace of 2 by 2 sparse matrices over Univariate Polynomial Ring in x over Rational Field
            sage: parent(A/2)
            Full MatrixSpace of 2 by 2 sparse matrices over Rational Field
        """
        from sage.categories.pushout import MatrixFunctor
        return MatrixFunctor(self.__nrows, self.__ncols, is_sparse=self.is_sparse()), self.base_ring()

    def get_action_impl(self, S, op, self_on_left):
        try:
            if op is operator.mul:
                import action as matrix_action
                if self_on_left:
                    if is_MatrixSpace(S):
                        return matrix_action.MatrixMatrixAction(self, S)
                    elif sage.modules.free_module.is_FreeModule(S):
                        return matrix_action.MatrixVectorAction(self, S)
                    else:
                        # action of base ring
                        return sage.structure.coerce.RightModuleAction(S, self)
                else:
                    if sage.modules.free_module.is_FreeModule(S):
                        return matrix_action.VectorMatrixAction(self, S)
                    else:
                        # action of base ring
                        return sage.structure.coerce.LeftModuleAction(S, self)
            else:
                return None
        except TypeError:
            return None

    def _coerce_impl(self, x):
        """
        EXAMPLES::
        
            sage: MS1 = MatrixSpace(QQ,3)
            sage: MS2 = MatrixSpace(ZZ,4,5,true)
            sage: A = MS1(range(9))
            sage: D = MS2(range(20))
            sage: MS1._coerce_(A)
            [0 1 2]
            [3 4 5]
            [6 7 8]
            sage: MS2._coerce_(D)
            [ 0  1  2  3  4]
            [ 5  6  7  8  9]
            [10 11 12 13 14]
            [15 16 17 18 19]
        """
        if isinstance(x, matrix.Matrix):
            if self.is_sparse() and x.is_dense():
                raise TypeError("cannot coerce dense matrix into sparse space for arithmetic")
            if x.nrows() == self.nrows() and x.ncols() == self.ncols():
                if self.base_ring().has_coerce_map_from(x.base_ring()):
                    return self(x)
                raise TypeError("no canonical coercion")
        return self._coerce_try(x, self.base_ring())

    def __cmp__(self, other):
        """
        Compare this matrix space with other. Sparse and dense matrix
        spaces with otherwise the same parameters are considered equal.
        
        If other is not a matrix space, return something arbitrary but
        deterministic. Otherwise, compare based on base ring, then on
        number of rows and columns.
        
        EXAMPLES::
        
            sage: Mat(ZZ,1000) == Mat(QQ,1000)
            False
            sage: Mat(ZZ,10) == Mat(ZZ,10)
            True
            sage: Mat(ZZ,10, sparse=False) == Mat(ZZ,10, sparse=True)
            True
        """
        if isinstance(other, MatrixSpace_generic):
            return cmp((self.base_ring(), self.__nrows, self.__ncols),
                       (other.base_ring(), other.__nrows, other.__ncols))
        return cmp(type(self), type(other))
        
    def _repr_(self):
        """
        Returns the string representation of a MatrixSpace
        
        EXAMPLES::
        
            sage: MS = MatrixSpace(ZZ,2,4,true)
            sage: repr(MS)
            'Full MatrixSpace of 2 by 4 sparse matrices over Integer Ring'
            sage: MS
            Full MatrixSpace of 2 by 4 sparse matrices over Integer Ring
        """
        if self.is_sparse():
            s = "sparse"
        else:
            s = "dense"
        return "Full MatrixSpace of %s by %s %s matrices over %s"%(
                    self.__nrows, self.__ncols, s, self.base_ring())

    def _latex_(self):
        r"""
        Returns the latex representation of a MatrixSpace
        
        EXAMPLES::
        
            sage: MS3 = MatrixSpace(QQ,6,6,true)
            sage: latex(MS3)
            \mathrm{Mat}_{6\times 6}(\Bold{Q})
        """
        return "\\mathrm{Mat}_{%s\\times %s}(%s)"%(self.nrows(), self.ncols(),
                                                      latex.latex(self.base_ring()))

    def __len__(self):
        """
        Return number of elements of this matrix space if it fits in
        an int; raise a TypeError if there are infinitely many
        elements, and raise an OverflowError if there are finitely
        many but more than the size of an int.
        
        EXAMPLES::

            sage: len(MatrixSpace(GF(3),3,2))
            729
            sage: len(MatrixSpace(GF(3),2,3))
            729
            sage: 3^(2*3)
            729
            sage: len(MatrixSpace(GF(2003),3,2))
            Traceback (most recent call last):
            ...
            OverflowError: long int too large to convert to int
            sage: len(MatrixSpace(QQ,3,2))
            Traceback (most recent call last):
            ...
            TypeError: len() of unsized object
        """
        return len(self.base_ring())**(self.nrows()*self.ncols())

    def __iter__(self):
        r"""
        Returns a generator object which iterates through the elements of
        self. The order in which the elements are generated is based on a
        'weight' of a matrix which is the number of iterations on the base
        ring that are required to reach that matrix.
        
        The ordering is similar to a degree negative lexicographic order in
        monomials in a multivariate polynomial ring.
        
        EXAMPLES: Consider the case of 2 x 2 matrices over GF(5).
        
        ::
        
            sage: list( GF(5) )
            [0, 1, 2, 3, 4]
            sage: MS = MatrixSpace(GF(5), 2, 2)
            sage: l = list(MS)
        
        Then, consider the following matrices::
        
            sage: A = MS([2,1,0,1]); A
            [2 1]
            [0 1]
            sage: B = MS([1,2,1,0]); B
            [1 2]
            [1 0]
            sage: C = MS([1,2,0,0]); C
            [1 2]
            [0 0]
        
        A appears before B since the weight of one of A's entries exceeds
        the weight of the corresponding entry in B earliest in the list.
        
        ::
        
            sage: l.index(A)
            41
            sage: l.index(B)
            46
        
        However, A would come after the matrix C since C has a lower weight
        than A.
        
        ::
        
            sage: l.index(A)
            41
            sage: l.index(C)
            19
        
        The weights of matrices over other base rings are not as obvious.
        For example, the weight of
        
        ::
        
            sage: MS = MatrixSpace(ZZ, 2, 2)
            sage: MS([-1,0,0,0])
            [-1  0]
            [ 0  0]
        
        is 2 since
        
        ::
        
            sage: i = iter(ZZ)
            sage: i.next()
            0
            sage: i.next()
            1
            sage: i.next()
            -1
        
        Some more examples::
        
            sage: MS = MatrixSpace(GF(2),2)
            sage: a = list(MS)
            sage: len(a)
            16
            sage: for m in a: print m, '\n-'
            [0 0]
            [0 0] 
            -
            [1 0]
            [0 0] 
            -
            [0 1]
            [0 0] 
            -
            [0 0]
            [1 0] 
            -
            [0 0]
            [0 1] 
            -
            [1 1]
            [0 0] 
            -           
            [1 0]
            [1 0] 
            -
            [1 0]
            [0 1] 
            -
            [0 1]
            [1 0] 
            -
            [0 1]
            [0 1] 
            -
            [0 0]
            [1 1] 
            -
            [1 1]
            [1 0] 
            -
            [1 1]
            [0 1] 
            -
            [1 0]
            [1 1] 
            -
            [0 1]
            [1 1] 
            -
            [1 1]
            [1 1] 
            -
        
        ::
        
            sage: MS = MatrixSpace(GF(2),2, 3)
            sage: a = list(MS)
            sage: len(a)
            64
            sage: a[0]
            [0 0 0]
            [0 0 0]
        
        ::
        
            sage: MS = MatrixSpace(ZZ, 2, 3)
            sage: i = iter(MS)
            sage: a = [ i.next() for _ in range(6) ]
            sage: a[0]
            [0 0 0]
            [0 0 0]
            sage: a[4]
            [0 0 0]
            [1 0 0]
        
        For degenerate cases, where either the number of rows or columns
        (or both) are zero, then the single element of the space is
        returned.
        
        ::
        
            sage: list( MatrixSpace(GF(2), 2, 0) )
            [[]]
            sage: list( MatrixSpace(GF(2), 0, 2) )
            [[]]
            sage: list( MatrixSpace(GF(2), 0, 0) )
            [[]]
        
        If the base ring does not support iteration (for example, with the
        reals), then the matrix space over that ring does not support
        iteration either.
        
        ::
        
            sage: MS = MatrixSpace(RR, 2)
            sage: a = list(MS)
            Traceback (most recent call last):
            ...
            NotImplementedError: object does not support iteration
        """
        #Make sure that we can iterate over the base ring
        base_ring = self.base_ring()
        base_iter = iter(base_ring)

        number_of_entries = (self.__nrows*self.__ncols)

        #If the number of entries is zero, then just
        #yield the empty matrix in that case and return
        if number_of_entries == 0:
            yield self(0)
            raise StopIteration
        
        import sage.combinat.integer_vector

        if not base_ring.is_finite():
            #When the base ring is not finite, then we should go
            #through and yield the matrices by "weight", which is
            #the total number of iterations that need to be done
            #on the base ring to reach the matrix.
            base_elements = [ base_iter.next() ]
            weight = 0
            while True:
                for iv in sage.combinat.integer_vector.IntegerVectors(weight, number_of_entries):
                    yield self(entries=[base_elements[i] for i in iv], rows=True)        
                        
                weight += 1
                base_elements.append( base_iter.next() )
        else:
            #In the finite case, we do a similar thing except that
            #the "weight" of each entry is bounded by the number
            #of elements in the base ring
            order = base_ring.order()
            done = False
            base_elements = list(base_ring)
            for weight in range((order-1)*number_of_entries+1):
                for iv in sage.combinat.integer_vector.IntegerVectors(weight, number_of_entries, max_part=(order-1)):
                   yield self(entries=[base_elements[i] for i in iv], rows=True)

          
    def _get_matrix_class(self):
        """
        Returns the class of self
        
        EXAMPLES::
        
            sage: MS1 = MatrixSpace(QQ,4)
            sage: MS2 = MatrixSpace(ZZ,4,5,true)
            sage: MS1._get_matrix_class()
            <type 'sage.matrix.matrix_rational_dense.Matrix_rational_dense'>
            sage: MS2._get_matrix_class()
            <type 'sage.matrix.matrix_integer_sparse.Matrix_integer_sparse'>
            sage: type(matrix(SR, 2, 2, 0))
            <type 'sage.matrix.matrix_symbolic_dense.Matrix_symbolic_dense'>
        """
        R = self.base_ring()
        if self.is_dense():
            if sage.rings.integer_ring.is_IntegerRing(R):
                return matrix_integer_dense.Matrix_integer_dense
            elif sage.rings.rational_field.is_RationalField(R):
                return matrix_rational_dense.Matrix_rational_dense
            elif sage.rings.number_field.number_field.is_CyclotomicField(R):
                import matrix_cyclo_dense
                return matrix_cyclo_dense.Matrix_cyclo_dense
            elif R==sage.rings.real_double.RDF:
                import matrix_real_double_dense
                return matrix_real_double_dense.Matrix_real_double_dense
            elif R==sage.rings.complex_double.CDF:
                import matrix_complex_double_dense
                return matrix_complex_double_dense.Matrix_complex_double_dense
            elif sage.rings.finite_rings.integer_mod_ring.is_IntegerModRing(R) and R.order() < matrix_modn_dense.MAX_MODULUS:
                if R.order() == 2:
                    return matrix_mod2_dense.Matrix_mod2_dense
                return matrix_modn_dense.Matrix_modn_dense
            elif sage.rings.polynomial.multi_polynomial_ring_generic.is_MPolynomialRing(R) and R.base_ring().is_field():
                return matrix_mpolynomial_dense.Matrix_mpolynomial_dense
            #elif isinstance(R, sage.rings.padics.padic_ring_capped_relative.pAdicRingCappedRelative):
            #    return padics.matrix_padic_capped_relative_dense
            # the default      
            else:
                from sage.symbolic.ring import SR   # causes circular imports
                if R is SR:
                    import matrix_symbolic_dense
                    return matrix_symbolic_dense.Matrix_symbolic_dense
                return matrix_generic_dense.Matrix_generic_dense
        
        else:            
            if sage.rings.finite_rings.integer_mod_ring.is_IntegerModRing(R) and R.order() < matrix_modn_sparse.MAX_MODULUS:
                return matrix_modn_sparse.Matrix_modn_sparse
            elif sage.rings.rational_field.is_RationalField(R):
                return matrix_rational_sparse.Matrix_rational_sparse
            elif sage.rings.integer_ring.is_IntegerRing(R):
                return matrix_integer_sparse.Matrix_integer_sparse
            # the default
            return matrix_generic_sparse.Matrix_generic_sparse
            
        
    def basis(self):
        """
        Returns a basis for this matrix space.
        
        .. warning::

           This will of course compute every generator of this matrix
           space. So for large matrices, this could take a long time,
           waste a massive amount of memory (for dense matrices), and
           is likely not very useful. Don't use this on large matrix
           spaces.
        
        EXAMPLES::
        
            sage: Mat(ZZ,2,2).basis()
            [
            [1 0]  [0 1]  [0 0]  [0 0]
            [0 0], [0 0], [1 0], [0 1]
            ]
        """
        v = [self.zero_matrix().__copy__() for _ in range(self.dimension())]
        one = self.base_ring()(1)
        i = 0
        for r in range(self.__nrows):
            for c in range(self.__ncols):
                v[i][r,c] = one
                v[i].set_immutable()
                i += 1
        return Sequence(v, universe=self, check=False, immutable=True, cr=True)

    def dimension(self):
        """
        Returns (m rows) \* (n cols) of self as Integer
        
        EXAMPLES::
        
            sage: MS = MatrixSpace(ZZ,4,6)
            sage: u = MS.dimension()
            sage: u - 24 == 0
            True
        """
        return self.__nrows * self.__ncols
    
    def dims(self):
        """
        Returns (m row, n col) representation of self dimension
        
        EXAMPLES::
        
            sage: MS = MatrixSpace(ZZ,4,6)
            sage: MS.dims()
            (4, 6)
        """
        return (self.__nrows, self.__ncols)

    from sage.misc.cachefunc import cached_method
    @cached_method
    def identity_matrix(self):
        """
        Returns the identity matrix in ``self``.

        ``self`` must be a space of square
        matrices. The returned matrix is immutable. Please use ``copy`` if
        you want a modified copy.

        EXAMPLES::

            sage: MS1 = MatrixSpace(ZZ,4)
            sage: MS2 = MatrixSpace(QQ,3,4)
            sage: I = MS1.identity_matrix()
            sage: I
            [1 0 0 0]
            [0 1 0 0]
            [0 0 1 0]
            [0 0 0 1]
            sage: Er = MS2.identity_matrix()
            Traceback (most recent call last):
            ...
            TypeError: self must be a space of square matrices

        TESTS::

            sage: MS1.one()[1,2] = 3
            Traceback (most recent call last):
            ...
            ValueError: matrix is immutable; please change a copy instead (i.e., use copy(M) to change a copy of M).
        """
        if self.__nrows != self.__ncols:
            raise TypeError("self must be a space of square matrices")
        A = self.zero_matrix().__copy__()
        for i in xrange(self.__nrows):
            A[i,i] = 1
        A.set_immutable()
        return A

    one = identity_matrix
    
    def is_dense(self):
        """
        Returns True if matrices in self are dense and False otherwise.
        
        EXAMPLES::
        
            sage: Mat(RDF,2,3).is_sparse()
            False
            sage: Mat(RR,123456,22,sparse=True).is_sparse()
            True
        """
        return not self.__is_sparse
        
    def is_sparse(self):
        """
        Returns True if matrices in self are sparse and False otherwise.
        
        EXAMPLES::
        
            sage: Mat(GF(2011),10000).is_sparse()
            False
            sage: Mat(GF(2011),10000,sparse=True).is_sparse()
            True
        """
        return self.__is_sparse
        
    def is_finite(self):
        """
        EXAMPLES::
        
            sage: MatrixSpace(GF(101), 10000).is_finite()
            True
            sage: MatrixSpace(QQ, 2).is_finite()
            False
        """
        return self.base_ring().is_finite()

    def gen(self, n):
        """
        Return the n-th generator of this matrix space.
        
        This doesn't compute all basis matrices, so it is reasonably
        intelligent.
        
        EXAMPLES::
        
            sage: M = Mat(GF(7),10000,5); M.ngens()
            50000
            sage: a = M.10
            sage: a[:4]
            [0 0 0 0 0]
            [0 0 0 0 0]
            [1 0 0 0 0]
            [0 0 0 0 0]
        """
        if hasattr(self, '__basis'):
            return self.__basis[n]
        r = n // self.__ncols
        c = n - (r * self.__ncols)
        z = self.zero_matrix().__copy__()
        z[r,c] = 1
        return z

    @cached_method
    def zero_matrix(self):
        """
        Returns the zero matrix in ``self``.

        ``self`` must be a space of square matrices. The returned matrix is
        immutable. Please use ``copy`` if you want a modified copy.

        EXAMPLES::

            sage: z = MatrixSpace(GF(7),2,4).zero_matrix(); z
            [0 0 0 0]
            [0 0 0 0]
            sage: z.is_mutable()
            False
            
        TESTS::

            sage: MM = MatrixSpace(RDF,1,1,sparse=False); mat = MM.zero_matrix()
            sage: copy(mat)
            [0.0]
            sage: MM = MatrixSpace(RDF,0,0,sparse=False); mat = MM.zero_matrix()
            sage: copy(mat)
            []
            sage: mat.is_mutable()
            False
            sage: MM.zero().is_mutable()
            False
        """
        res = self.__matrix_class(self, 0, coerce=False, copy=False)
        res.set_immutable()
        return res

    zero = zero_matrix
    
    def ngens(self):
        """
        Return the number of generators of this matrix space, which is the
        number of entries in the matrices in this space.
        
        EXAMPLES::
        
            sage: M = Mat(GF(7),100,200); M.ngens()
            20000
        """
        return self.dimension()

    def matrix(self, x=0, coerce=True, copy=True, rows=True):
        """
        Create a matrix in self. The entries can be specified either as a
        single list of length nrows\*ncols, or as a list of lists.
        
        EXAMPLES::
        
            sage: M = MatrixSpace(ZZ, 2)
            sage: M.matrix([[1,0],[0,-1]])
            [ 1  0]
            [ 0 -1]
            sage: M.matrix([1,0,0,-1])
            [ 1  0]
            [ 0 -1]
            sage: M.matrix([1,2,3,4])
            [1 2]
            [3 4]
            sage: M.matrix([1,2,3,4],rows=False)
            [1 3]
            [2 4]
        """
        if isinstance(x, (types.GeneratorType, xrange)):
            x = list(x)
        elif isinstance(x, (int, integer.Integer)) and x==1:
            return self.identity_matrix().__copy__()
        if matrix.is_Matrix(x):
            if x.parent() is self:
                if x.is_immutable():
                    return x
                else:
                    return x.__copy__()
            x = x.list()
        if isinstance(x, list) and len(x) > 0:
            if isinstance(x[0], list):
                x = sum(x,[])
            elif hasattr(x[0], "is_vector"): # TODO: is this the best way to test that?
                e = []
                for v in x:
                    e = e + v.list()
                copy = False # deep copy?
                x = e
            elif isinstance(x[0], tuple):
                x = list(sum(x,()))

            if not rows:
                new_x = []
                for k in range(len(x)):
                    i = k % self.__ncols
                    j = k // self.__ncols
                    new_x.append( x[ i*self.__nrows + j ] )
                x = new_x
            
        return self.__matrix_class(self, entries=x, copy=copy, coerce=coerce) 
     
    def matrix_space(self, nrows=None, ncols=None, sparse=False):
        """
        Return the matrix space with given number of rows, columns and
        sparcity over the same base ring as self, and defaults the same as
        self.
        
        EXAMPLES::
        
            sage: M = Mat(GF(7),100,200)
            sage: M.matrix_space(5000)
            Full MatrixSpace of 5000 by 200 dense matrices over Finite Field of size 7
            sage: M.matrix_space(ncols=5000)
            Full MatrixSpace of 100 by 5000 dense matrices over Finite Field of size 7
            sage: M.matrix_space(sparse=True)
            Full MatrixSpace of 100 by 200 sparse matrices over Finite Field of size 7
        """
        if nrows is None:
            nrows = self.__nrows
        if ncols is None:
            ncols = self.__ncols
        base = self._base
        try:
            MS = _cache[base,nrows,ncols,sparse]()
        except KeyError:
            return MatrixSpace(base, nrows, ncols, sparse=sparse)
        if MS is not None:
            return MS
        return MatrixSpace(base, nrows, ncols, sparse=sparse)

    def ncols(self):
        """
        Return the number of columns of matrices in this space.
        
        EXAMPLES::
        
            sage: M = Mat(ZZ['x'],200000,500000,sparse=True)
            sage: M.ncols()
            500000
        """
        return self.__ncols
        
    def nrows(self):
        """
        Return the number of rows of matrices in this space.
        
        EXAMPLES::
        
            sage: M = Mat(ZZ,200000,500000)
            sage: M.nrows()
            200000
        """
        return self.__nrows

    def row_space(self):
        """
        Return the module spanned by all rows of matrices in this matrix
        space. This is a free module of rank the number of rows. It will be
        sparse or dense as this matrix space is sparse or dense.
        
        EXAMPLES::
        
            sage: M = Mat(ZZ,20,5,sparse=False); M.row_space()
            Ambient free module of rank 5 over the principal ideal domain Integer Ring
        """
        try:
            return self.__row_space
        except AttributeError:
            self.__row_space = sage.modules.free_module.FreeModule(self.base_ring(),
                                                self.ncols(), sparse=self.is_sparse())
            return self.__row_space
    
    def column_space(self):
        """
        Return the module spanned by all columns of matrices in this matrix
        space. This is a free module of rank the number of columns. It will
        be sparse or dense as this matrix space is sparse or dense.
        
        EXAMPLES::
        
            sage: M = Mat(GF(9,'a'),20,5,sparse=True); M.column_space()
            Sparse vector space of dimension 20 over Finite Field in a of size 3^2
        """
        try:
            return self.__column_space
        except AttributeError:
            self.__column_space = sage.modules.free_module.FreeModule(self.base_ring(), self.nrows(),
                                                                   sparse=self.is_sparse())
            return self.__column_space

    def random_element(self, density=None, *args, **kwds):
        """
        Returns a random element from this matrix space.
        
        INPUT:
        
        -  ``density`` - ``float`` or ``None`` (default: ``None``);  rough 
           measure of the proportion of nonzero entries in the random matrix; 
           if set to ``None``, all entries of the matrix are randomized, 
           allowing for any element of the underlying ring, but if set to 
           a ``float``, a proportion of entries is selected and randomized to 
           non-zero elements of the ring
        
        -  ``*args, **kwds`` - remaining parameters, which may be passed to 
           the random_element function of the base ring. ("may be", since this 
           function calls the ``randomize`` function on the zero matrix, which 
           need not call the ``random_element`` function of the base ring at 
           all in general.)
        
        OUTPUT:
        
        -  Matrix
        
        NOTES:
        
        This method will randomize a proportion of roughly ``density`` entries 
        in a newly allocated zero matrix.
        
        By default, if the user sets the value of ``density`` explicitly, this 
        method will enforce that these entries are set to non-zero values.  
        However, if the test for equality with zero in the base ring is too 
        expensive, the user can override this behaviour by passing the 
        argument ``nonzero=False`` to this method.
        
        Otherwise, if the user does not set the value of ``density``, the 
        default value is taken to be 1, and the option ``nonzero=False`` is 
        passed to the ``randomize`` method.
        
        EXAMPLES::
        
            sage: Mat(ZZ,2,5).random_element()
            [ -8   2   0   0   1]
            [ -1   2   1 -95  -1]
            sage: Mat(QQ,2,5).random_element(density=0.5)
            [ 2  0  0  0  1]
            [ 0  0  0 -1  0]
            sage: Mat(QQ,3,sparse=True).random_element()
            [  -1   -1   -1]
            [  -3 -1/3   -1]
            [   0   -1    1]
            sage: Mat(GF(9,'a'),3,sparse=True).random_element()
            [    2*a       a       1]
            [      2       1 2*a + 1]
            [      a       2       2]
        """
        Z = self.zero_matrix().__copy__()
        if density is None:
            Z.randomize(density=float(1), nonzero=kwds.pop('nonzero', False), \
                *args, **kwds)
        else:
            Z.randomize(density=density, nonzero=kwds.pop('nonzero', True), \
                *args, **kwds)
        return Z

    def _magma_init_(self, magma):
        r"""
        EXAMPLES: We first coerce a square matrix.
        
        ::
        
            sage: magma(MatrixSpace(QQ,3))                      # optional - magma
            Full Matrix Algebra of degree 3 over Rational Field
        
        ::
        
            sage: magma(MatrixSpace(Integers(8),2,3))           # optional - magma
            Full RMatrixSpace of 2 by 3 matrices over IntegerRing(8)
        """
        K = magma(self.base_ring())
        if self.__nrows == self.__ncols:
            s = 'MatrixAlgebra(%s,%s)'%(K.name(), self.__nrows)
        else:
            s = 'RMatrixSpace(%s,%s,%s)'%(K.name(), self.__nrows, self.__ncols)
        return s

def dict_to_list(entries, nrows, ncols):
    """
    Given a dictionary of coordinate tuples, return the list given by
    reading off the nrows\*ncols matrix in row order.
    
    EXAMPLES::
    
        sage: from sage.matrix.matrix_space import dict_to_list
        sage: d = {}
        sage: d[(0,0)] = 1
        sage: d[(1,1)] = 2
        sage: dict_to_list(d, 2, 2)
        [1, 0, 0, 2]
        sage: dict_to_list(d, 2, 3)
        [1, 0, 0, 0, 2, 0]
    """
    v = [0]*(nrows*ncols)
    for ij, y in entries.iteritems():
        i,j = ij
        v[i*ncols + j] = y
    return v

def list_to_dict(entries, nrows, ncols, rows=True):
    """
    Given a list of entries, create a dictionary whose keys are
    coordinate tuples and values are the entries.
    
    EXAMPLES::
    
        sage: from sage.matrix.matrix_space import list_to_dict
        sage: d = list_to_dict([1,2,3,4],2,2)
        sage: d[(0,1)]
        2
        sage: d = list_to_dict([1,2,3,4],2,2,rows=False)
        sage: d[(0,1)]
        3
    """
    d = {}
    if ncols == 0 or nrows == 0:
        return d
    for i in range(len(entries)):
        x = entries[i]
        if x != 0:
            col = i % ncols
            row = i // ncols
            if rows:
                d[(row,col)] = x
            else:
                d[(col,row)] = x
    return d



# sage: m = matrix(F, 0,0, sparse=False)
# sage: m.determinant()
# 0


def test_trivial_matrices_inverse(ring, sparse=True, checkrank=True):
    """
    Tests inversion, determinant and is_invertible for trivial matrices. 
    
    This function is a helper to check that the inversion of trivial matrices
    (of size 0x0, nx0, 0xn or 1x1) is handled consistently by the various
    implementation of matrices. The coherency is checked through a bunch of
    assertions. If an inconsistency is found, an AssertionError is raised
    which should make clear what is the problem.
    
    INPUT:
    
    - ``ring`` - a ring
    - ``sparse`` - a boolean
    - ``checkrank`` - a boolean
    
    OUTPUT:
    
    - nothing if everything is correct, otherwise raise an AssertionError
    
    The methods determinant, is_invertible, rank and inverse are checked for
     - the 0x0 empty identity matrix
     - the 0x3 and 3x0 matrices
     - the 1x1 null matrix [0]
     - the 1x1 identity matrix [1]
    
    If ``checkrank`` is ``False`` then the rank is not checked. This is used
    the check matrix over ring where echelon form is not implemented. 
    
    TODO: must be adapted to category check framework when ready (see trac \#5274).
    
    TESTS::
    
        sage: from sage.matrix.matrix_space import test_trivial_matrices_inverse as tinv
        sage: tinv(ZZ, sparse=True)
        sage: tinv(ZZ, sparse=False)
        sage: tinv(QQ, sparse=True)
        sage: tinv(QQ, sparse=False)
        sage: tinv(GF(11), sparse=True)
        sage: tinv(GF(11), sparse=False)
        sage: tinv(GF(2), sparse=True)
        sage: tinv(GF(2), sparse=False)
        sage: tinv(SR, sparse=True)
        sage: tinv(SR, sparse=False)
        sage: tinv(RDF, sparse=True)
        sage: tinv(RDF, sparse=False)
        sage: tinv(CDF, sparse=True)
        sage: tinv(CDF, sparse=False)
        sage: tinv(CyclotomicField(7), sparse=True)
        sage: tinv(CyclotomicField(7), sparse=False)
        sage: tinv(QQ['x,y'], sparse=True)
    
   TODO: As soon as rank of dense matrix over QQ['x,y'] is implemented,
   please remove the following test and the ``checkrank=False`` in the next one:
      
        sage: MatrixSpace(QQ['x,y'], 3, 3, sparse=False)(1).rank()
        Traceback (most recent call last):
        ...
        RuntimeError: BUG: matrix pivots should have been set but weren't, matrix parent = 'Full MatrixSpace of 3 by 3 dense matrices over Multivariate Polynomial Ring in x, y over Rational Field'
        
        sage: tinv(QQ['x,y'], sparse=False, checkrank=False)
    
    """
    # Check that the empty 0x0 matrix is it's own inverse with det=1. 
    ms00 = MatrixSpace(ring, 0, 0, sparse=sparse)
    m00  = ms00(0)
    assert(m00.determinant() == ring(1))
    assert(m00.is_invertible())
    assert(m00.inverse() == m00)
    if checkrank:
        assert(m00.rank() == 0)

    # Check that the empty 0x3 and 3x0 matrices are not invertible and that
    # computing the determinant raise the proper exception. 
    for ms0 in [MatrixSpace(ring, 0, 3, sparse=sparse),
                MatrixSpace(ring, 3, 0, sparse=sparse)]:
        mn0  = ms0(0)
        assert(not mn0.is_invertible())
        try:
            d = mn0.determinant()
            print d
            res = False
        except ValueError:
            res = True
        assert(res)
        try:
            mn0.inverse()
            res =False
        except ArithmeticError:
            res = True
        assert(res)
        if checkrank:
            assert(mn0.rank() == 0)

    # Check that the null 1x1 matrix is not invertible and that det=0
    ms1 = MatrixSpace(ring, 1, 1, sparse=sparse)
    m0  = ms1(0)
    assert(not m0.is_invertible())
    assert(m0.determinant() == ring(0))
    try:
        m0.inverse()
        res = False
    except (ZeroDivisionError, RuntimeError):
        #FIXME: Make pynac throw a ZeroDivisionError on division by
        #zero instead of a runtime Error
        res = True
    assert(res)
    if checkrank:
        assert(m0.rank() == 0)

    # Check that the identity 1x1 matrix is its own inverse with det=1
    m1  = ms1(1)
    assert(m1.is_invertible())
    assert(m1.determinant() == ring(1))
    inv = m1.inverse()
    assert(inv == m1)
    if checkrank:
        assert(m1.rank() == 1)
