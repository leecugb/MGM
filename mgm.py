#代码改编自http://www.planetary.brown.edu/mgm/
import numpy as np
wconst = 2.354820
def init(points):
    rmslim, rimplim = [0.002, 0.1E-04]
    cp = np.array([0.47227115E+00,  -0.124962712E-05])
    sp = np.array([0.5, 0.1E-04 ])
    gcent=points
    #gcent=np.array([8700,8800,9000,9150,9300,9450])
    gfwhm = np.array([200]*len(points))
    gstr  = np.array([-0.4]*len(points))
    scent = np.array([100]*len(points))
    sfwhm = np.array([300]*len(points))
    sstr  = np.array([10]*len(points))
    nbands =len(gcent)
    nparam = 3*nbands + 2
    mstruc={}
    mstruc['cparam']  = cp[:2]
    mstruc['sparam']  = sp[:2]
    mstruc['rmslim']  = rmslim
    mstruc['rimplim'] = rimplim
    mstruc['gcent']   = gcent
    mstruc['gfwhm']   = gfwhm
    mstruc['gstr']    = gstr
    mstruc['scent']   = scent
    mstruc['sfwhm']   = sfwhm
    mstruc['sstr']    = sstr
    mstruc['gwidth'] = mstruc['gfwhm']/wconst
    mstruc['gcentn'] = 1.0E7 /( mstruc['gcent'] ) # convert to wavenumber
    params = np.zeros( nparam )
    params[:nbands] = mstruc['gcentn']
    params[nbands:2*nbands] = mstruc['gwidth']
    params[2*nbands:3*nbands] = mstruc['gstr']
    params[nparam-2:nparam] = mstruc['cparam']
    mstruc['params']  = params
    mstruc['nparam']  = nparam
    mstruc['nbands']  = nbands
    mstruc['std']     = np.zeros(nparam)
#######################################
    cmm = np.zeros(nparam)
    mstruc['scent']=1.0E7 /(mstruc['gcent']-mstruc['scent'])-1.0E7 /(mstruc['gcent']+mstruc['scent'])
    mstruc['sfwhm'] = mstruc['sfwhm']/wconst
    cmm[:nbands] = mstruc['scent']
    cmm[nbands:2*nbands] = mstruc['sfwhm']
    cmm[2*nbands:3*nbands] = mstruc['sstr']
    cmm[nparam-2:nparam] = mstruc['sparam']
    mstruc['cmm'] = cmm
    ipstat = np.zeros( nparam )
    ipstat[:nbands ] = 1
    ipstat[nbands:2*nbands ] = 2
    ipstat[2*nbands:3*nbands ] = 3
    ipstat[nparam-2:nparam ] = [4,5]
    mstruc['ipstat'] = ipstat
   ############################################## 
    datarr=data
    sz =  datarr.shape
    errors='n'
    if sz[1] > 2:
        errors=input(' Use Errorbars (y or n) ?   ')
    if errors=='Y' or errors=='y':
        daterror = datarr[:,2]
    else:
        daterror = np.ones( sz[0] )
    ratio = np.log( datarr[:,1] )
    wavel = datarr[:,0]
    waven = 1.0E7 /( wavel ) 
    npnts = len( ratio )
    datstruc={}
    datstruc['ratio']   = ratio
    datstruc['wavel']   = wavel
    datstruc['waven']   = waven
    datstruc['daterror'] = daterror
    datstruc['fit']  = np.zeros(npnts)
    datstruc['cont'] = np.zeros(npnts)
    datstruc['resid'] = np.zeros(npnts)
    datstruc['rcont']  = np.zeros(npnts)
    datstruc['gline']    = np.zeros(npnts)
    datstruc['gauss']    = np.zeros([npnts,nbands])
    datstruc['npnts']    = npnts
    return mstruc, datstruc

def cgauss(x0, width, zintens, x):
# CGAUSS(X0, width, str, X) gives the gaussian distribution over the elements
# of X.
# X0 = gaussian center
# width = full-width half maximum
# zintens = strength or amplitude
    xdif  = x - x0                 		# ROOTS PRECALCULATED
    xsq   = xdif * xdif
    sigsq = width
    c = zintens * np.exp(xsq/sigsq)
    return c

def unshuffl(mstruc):
    nbands=mstruc['nbands']
    mstruc['gcentn'] = mstruc['params'][:nbands]
    mstruc['gwidth'] = mstruc['params'][nbands:2*nbands]
    mstruc['gfwhm']  = mstruc['gwidth'] * wconst
    mstruc['gstr']   = mstruc['params'][2*nbands:3*nbands]
    mstruc['gcent'] = 1.0E7 /( mstruc['gcentn'] )
    mstruc['cparam'] = mstruc['params'][ mstruc['nparam']-2:mstruc['nparam']]
    return mstruc

def fillup( mstruc, datstruc ):
    SGRT = mstruc['gwidth']  # to be determined
    gauss = np.zeros( [datstruc['npnts'], mstruc['nbands'] ])
    gauss=cgauss(mstruc['gcent'].reshape([1,-1]),
                 (-2*SGRT * SGRT).reshape([1,-1]),
                 mstruc['gstr'].reshape([1,-1]),
                 datstruc['wavel'].reshape([-1,1]))
    gline = gauss.sum(1)
    w = datstruc['waven']
    cont = mstruc['cparam'][0]+(mstruc['cparam'][1]*w)
    cont = np.log(cont)
    if np.isnan(cont).any():
        mstruc['cparam']=np.array([1,0])  
        cont = np.zeros( datstruc['npnts'] )# No Continuum
    fit = cont + gline
    resid = datstruc['ratio'] - fit
    rcont = datstruc['ratio'] - cont
    datstruc['gline']  = gline
    datstruc['cont']   = cont
    datstruc['gauss']  = gauss
    datstruc['fit']    = fit
    datstruc['resid']  = resid
    datstruc['rcont']  = rcont
    return mstruc, datstruc

def rmserr(arr1, arr2):
    dif   = arr1 - arr2
    sqr   = dif * dif
    tot   = sqr.sum()/len(arr1)
    r     = tot**0.5
    return r

class Der_error(ValueError):
    pass

def pgauss(x0, width, zintens, x, ipart):
    xdif = x - x0
    xsq  = xdif * xdif
    sigma= width
    sigsq= sigma * sigma
    if ipart==1:
        pg=(xdif/sigsq)*(-1.0*x0**2.0)/1.0E7
    elif ipart==2:
        pg=xsq/(sigsq*sigma)
    elif ipart==3:
        pg=1.0/zintens
    else:
        raise Der_error('No such partial derivative!')
    return pg

def stocfit( mstruc, datstruc, isampres ):
    ITR=0
    ddx=np.arange(0,datstruc['npnts'],isampres,dtype=int)
    keepgoing = 1
    nbands=mstruc['nbands']
    while keepgoing == 1:
        FACTI=1.0
        OLDPAR = mstruc['params']
        nparam = mstruc['nparam']
        G = np.zeros( [len(ddx), nparam] )
        G[:,0:nbands]=pgauss(mstruc['gcent'].reshape([1,-1]),mstruc['gwidth'].reshape([1,-1]),mstruc['gstr'].reshape([1,-1]),datstruc['wavel'][ddx].reshape([-1,1]),1)*datstruc['gauss'][ddx,:]
        G[:,nbands:2*nbands]=pgauss(mstruc['gcent'].reshape([1,-1]),mstruc['gwidth'].reshape([1,-1]),mstruc['gstr'].reshape([1,-1]),datstruc['wavel'][ddx].reshape([-1,1]),2)*datstruc['gauss'][ddx,:]
        G[:,2*nbands:3*nbands]=pgauss(mstruc['gcent'].reshape([1,-1]),mstruc['gwidth'].reshape([1,-1]),mstruc['gstr'].reshape([1,-1]),datstruc['wavel'][ddx].reshape([-1,1]),3)*datstruc['gauss'][ddx,:]
        G[:,3*nbands] = 1.0 / np.exp( datstruc['cont'][ddx] )
        G[:,3*nbands+1] = datstruc['waven'][ddx]   / np.exp( datstruc['cont'][ddx])
        cmminv = np.diag(1.0/(mstruc['cmm']/1.96)**2)
        if np.any(datstruc['daterror'] != 1):
            cnnvarinv= 1/(datstruc['daterror'][ddx]/(datstruc['daterror'][ddx]).mean())
        else:
            cnnvarinv=datstruc['daterror']
        cnninv = cnnvarinv.reshape([-1,1])[:,np.zeros(nparam,dtype='int')]
        gtgmminv = np.linalg.inv(G.T.dot(cnninv*G) + cmminv )
        MCHS = gtgmminv.dot((G.T.dot(cnnvarinv*datstruc['resid'][ddx]))     )
        rmsold = rmserr( datstruc['fit'][ddx],datstruc['ratio'][ddx] )
        mstruc['params'] = OLDPAR + MCHS
        mstruc = unshuffl( mstruc )
        mstruc, datstruc = fillup(mstruc,datstruc)
        rmsnew = rmserr(datstruc['fit'][ddx],datstruc['ratio'][ddx])
        mstruc,datstruc,keepgoing,ITR = error_check(mstruc,datstruc,rmsold,rmsnew,ITR,FACTI,OLDPAR,MCHS,ddx)
    gtginv = np.linalg.inv( G.T.dot(G ))
    mstruc['std'] =1.96 * np.sqrt( np.diag(gtginv) * rmsnew**2 )  
    return mstruc,datstruc

def error_check(mstruc,datstruc,rmsold,rmsnew,ITR,FACTI,OLDPAR,MCHS,ddx):
    failure = 1./(2.0**15)
    keepgoing = 1
    itry=0
    while (rmsnew >= rmsold):
        itry = itry + 1
        print(' Applying Binary Backoff to Correction  {:4d}'.format(itry ))
        FACTI = FACTI/2.0
        if (FACTI < failure):
            mstruc['params'] = OLDPAR
            mstruc = unshuffl( mstruc )
            mstruc, datstruc = fillup(mstruc,datstruc)
            print('  Interpolation by Binary Backoff Fails !!')
            keepgoing = 0
            return mstruc,datstruc,keepgoing,ITR
        else:
            mstruc['params'] = OLDPAR + (FACTI * MCHS)
            mstruc = unshuffl( mstruc )
            mstruc, datstruc = fillup( mstruc, datstruc )
            rmsnew = rmserr( datstruc['fit'][ddx], datstruc['ratio'][ddx] )
    ITR = ITR+1
    rmsimp = rmsold - rmsnew
    print('{:5d}   Old RMS{:14.6e}   New RMS={:14.6e}   Imp={:14.6e}'.format(ITR,rmsold,rmsnew,rmsimp))
    nnn = np.nonzero( mstruc['params'][:mstruc['nbands']]< 0)[0]
    [print('  Band #{:3d} has a negative centers !!!'.format(i+1)) for i in nnn]
    mstruc['params'][mstruc['nbands'] :2*mstruc['nbands'] ] = abs( mstruc['params'][ mstruc['nbands']:2*mstruc['nbands']])
    nnn = np.nonzero( mstruc['params'][2*mstruc['nbands']:3*mstruc['nbands']] > 0 )[0]
    [print( '  Band #{:3d} has a positive strength !!!'.format( i+1 )) for i in nnn]
    if (rmsimp <= mstruc['rimplim']):
        print( '  Improvement in rms less than limit !!' )
        keepgoing=0
    if (rmsnew <= mstruc['rmslim']):
        print( '  Rms less than limit !!' )
        keepgoing = 0
    return mstruc,datstruc,keepgoing,ITR

def process(mstruc, datstruc):
    mstruc, datstruc = fillup( mstruc, datstruc )
    iresl = abs( datstruc['wavel'][1] - datstruc['wavel'][0])
    if iresl < 1:
        iresl = 1
    ifitres  = iresl
    isampres = ifitres/iresl
    rmsold   = rmserr( datstruc['fit'], datstruc['ratio'] )
    fitflag  = 0
    DoAgain = 1
    print(iresl,isampres,rmsold)
    mstruc,datstruc = stocfit( mstruc, datstruc, isampres)
    return mstruc, datstruc
