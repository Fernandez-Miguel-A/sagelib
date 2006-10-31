# Optional versions of certain ring constructors that automatically
# inject variables into the global module scope.

import sage.rings.all

_verbose=True
_inject_mode_off = False

def inject_verbose(mode):
    global _verbose
    _verbose= mode

_original_constructors = None

def inject_on(verbose=True):
    """
    Replace several constructors by versions that inject their
    variables into the global namespace. 
    """
    global _original_constructors
    _original_constructors = {}
    import sage.ext.interactive_constructors_c 
    G = globals()
    if verbose:
        print "Redefining:",
    for X in sage.ext.interactive_constructors_c.__dict__.keys():
        if not 'inject' in X and X[0] != '_' and X[:4] != 'sage':
            if verbose:
                print X, 
            try:
                _original_constructors[X] =  sage.ext.interactive_constructors_c.__dict__[X]
            except KeyError:
                pass
            G[X] = sage.ext.interactive_constructors_c.__dict__[X]
    if verbose:
        print ""
        
def inject_off():
    global _original_constructors
    if not _original_constructors is None:
        for X in _original_constructors.keys():
            globals()[X] = _original_constructors[X]

cdef _inject(X, do):
    if do:
        X.inject_variables(verbose=_verbose)
    return X

cdef _do_inject(kwds):
    if kwds.has_key('inject'):
        s = kwds['inject']
        del kwds['inject']
        return s == True
    return True

def FiniteField(*args, **kwds):
    """
    Construct a finite field and inject the variables of the
    finite field to the global interactive interpreter.  Use
    inject=False to not inject the variables.  This is a wrapper
    around the following function: <<<FiniteField>>>
    """
    t = _do_inject(kwds)
    R = sage.rings.all.FiniteField(*args, **kwds)
    return _inject(R, t)

GF = FiniteField

def FractionField(*args, **kwds):
    """
    Construct the fraction field of a field and inject the generators
    of the fraction field to the global interactive interpreter.  Use
    inject=False to not inject the variables.  This is a wrapper
    around the following function: <<<FractionField>>>

    EXAMPLES (that illustrate interactive injection of variables):
        sage: Frac(QQ['x'])
        Fraction Field of Univariate Polynomial Ring in x over Rational Field
        sage: parent(x)
        Fraction Field of Univariate Polynomial Ring in x over Rational Field    
    """
    t = _do_inject(kwds)
    R = sage.rings.all.FractionField(*args, **kwds)
    return _inject(R, t)

Frac = FractionField


def FreeMonoid(*args, **kwds):
    """
    Construct a free monoid and inject the variables of the monoid
    into the global interactive interpreter.  Use inject=Fale to not
    inject the variables.  This is a wrapper around the following
    function: <<<FreeMonoid>>>

    MORE EXAMPLES:
    We illustrate creating a free monoid with and without injecting
    the variables into the interpreter.
    
        sage: FreeMonoid(4,'x')
        Free monoid on 4 generators (x0, x1, x2, x3)
        sage: x2
        x2
        sage: FreeMonoid(4,'y', inject=False)
        Free monoid on 4 generators (y0, y1, y2, y3)
        sage: y
        Traceback (most recent call last):
        ...
        NameError: name 'y' is not defined    
    """
    t = _do_inject(kwds)
    R = sage.monoids.free_monoid.FreeMonoid(*args, **kwds)
    return _inject(R, t)
    
def LaurentSeriesRing(*args, **kwds):
    """
    Construct the Laurent series ring over a ring, and inject the
    generator into the interpreter's global namespace.  Use
    inject=False to not inject the variables.  This is a wrapper
    around the following function:

    <<<LaurentSeries>>>
    """
    t = _do_inject(kwds)
    R = sage.rings.all.LaurentSeriesRing(*args, **kwds)
    return _inject(R, t)

def NumberField(*args, **kwds):
    """
    Construct a number field, and inject the generator of the number
    fraction field into the interpreters global namespace.  Use
    inject=False to not inject the variables.  This is a wrapper
    around the following function:
    <<<NumberField>>>
    """
    t = _do_inject(kwds)
    R = sage.rings.all.NumberField(*args, **kwds)
    return _inject(R, t)

def quotient(R, I, names, inject=True):
    """
    Construct the quotient R/I and name the generators, which are
    then injected into the module scope (if inject=True).

    EXAMPLES:
        sage: R = QQ['x,y']
        sage: S = quo(R, (x^3, x^2 + y^2), 'a,b')
        sage: S
        Quotient of Polynomial Ring in x, y over Rational Field by the ideal (y^2 + x^2, x^3)
        sage: a^2
        -1*b^2
        sage: a^3
        0
        sage: a^2 + b
        b - b^2
        sage: a^2 + b^2
        0    
    """
    Q = R.quotient(I, names)
    return _inject(Q, inject)

quo = quotient


def PolynomialRing(*args, **kwds):
    """
    Construct a polynomial ring and inject the variables of the
    polynomial ring to the global interactive interpreter.  Use
    inject=False to not inject the variables.  This is a wrapper
    around the following function: <<<PolynomialRing>>>

    MORE EXAMPLES:
    We illustrate creating a polynomial ring without injecting the variables
    into the interpreter.

        sage: PolynomialRing(QQ,'w')
        Univariate Polynomial Ring in w over Rational Field
        sage: parent(w)
        Univariate Polynomial Ring in w over Rational Field
        sage: PolynomialRing(GF(17), 'w', inject=False)
        Univariate Polynomial Ring in w over Finite Field of size 17
        sage: parent(w)
        Univariate Polynomial Ring in w over Rational Field
    """
    t = _do_inject(kwds)
    R = sage.rings.all.PolynomialRing(*args, **kwds)
    return _inject(R, t)



###################### need to add a bunch more ############################

