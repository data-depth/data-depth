import numpy as np
from ctypes import *
from multiprocessing import *
import sklearn.covariance as sk
import scipy.special as scspecial
import sys, os, glob
import platform

if sys.platform=='linux':
    for i in sys.path :
        if i.split('/')[-1]=='site-packages':
            ddalpha_exact=glob.glob(i+'/depth/UNIX/'+'ddalpha.so')
            ddalpha_approx=glob.glob(i+'/depth/UNIX/'+'depth_wrapper.so')
    

    libr=CDLL(ddalpha_exact[0])
    libRom=CDLL(ddalpha_approx[0])
    
if sys.platform=='darwin':
    for i in sys.path :
        if i.split('/')[-1]=='site-packages':
            ddalpha_exact=glob.glob(i+'/depth/MACOS/'+'ddalpha.so')
            ddalpha_approx=glob.glob(i+'/depth/MACOS/'+'depth_wrapper.so')
    

    libr=CDLL(ddalpha_exact[0])
    libRom=CDLL(ddalpha_approx[0])

if sys.platform=='win32' and platform.architecture()[0] == "64bit":
    site_packages = next(p for p in sys.path if 'site-packages' in p)
    print(site_packages)
    os.add_dll_directory(site_packages+"\depth\Win64")
    libr=CDLL(r""+site_packages+"\depth\Win64\ddalpha.dll")
    libRom=CDLL(r""+site_packages+"\depth\Win64\depth_wrapper.dll")
    
if sys.platform=='win32' and platform.architecture()[0] == "32bit":
    site_packages = next(p for p in sys.path if 'site-packages' in p)
    print(site_packages)
    os.add_dll_directory(site_packages+"\depth\Win32")
    libr=CDLL(r""+site_packages+"\depth\Win32\ddalpha.dll")
    libRom=CDLL(r""+site_packages+"\depth\Win32\depth_wrapper.dll")

def longtoint(k):
  limit = 2000000000
  k1 = int(k/limit)
  k2 = int(k - k1*limit)
  return np.array([k1,k2])

def MCD_fun(data,alpha,NeedLoc=False):
    cov = sk.MinCovDet(support_fraction=alpha).fit(data)
    if NeedLoc:return([cov.covariance_,cov.location_])
    else:return(cov.covariance_)

def simplicialVolume(x,data,exact=True,k=0.05,mah_estimate="moment", mah_parMCD=0.75,seed=0):
    points_list=data.flatten()
    objects_list=x.flatten()
    if (mah_estimate == "none"):
        useCov = 0
        covEst =np.eye(len(data[0])).flatten()
    elif (mah_estimate == "moment"):
        useCov = 1
        covEst=np.cov(np.transpose(data))
    
    elif (mah_estimate == "MCD") :
        useCov = 2
        covEst = MCD_fun(data, mah_parMCD)
    else:
        print("Wrong argument \"mah.estimate\", should be one of \"moment\", \"MCD\", \"none\"")
        print("moment is use")
        useCov = 1
        covEst=np.cov(data)
        
    points=(c_double*len(points_list))(*points_list)
    objects=(c_double*len(objects_list))(*objects_list)

    points=pointer(points)
    objects=pointer(objects)
    numPoints=pointer(c_int(len(data)))
    numObjects=pointer(c_int(len(x)))
    dimension=pointer(c_int(len(data[0])))
    
    seed=pointer((c_int(seed)))
    exact=pointer((c_int(exact)))
    if k<=0:
        print("k must be positive")
        print("k=1")
        k=scspecial.comb(len(data),len(data[0]),exact=True)*k
        k=pointer((c_int*2)(*longtoint(k)))
    elif k<=1:
        k=scspecial.comb(len(data),len(data[0]),exact=True)*k
        k1=k
        k=pointer((c_int*2)(*longtoint(k)))
    else:
        k=pointer((c_int*2)(*longtoint(k)))
        
    
    
    useCov=pointer(c_int(useCov))
    covEst=covEst.flatten()
    covEst=pointer((c_double*len(covEst))(*covEst))
        
    depths=pointer((c_double*len(x))(*np.zeros(len(x))))

    libr.OjaDepth(points,objects,numPoints,numObjects,dimension,seed, exact, k, useCov, covEst, depths)

    res=np.zeros(len(x))
    for i in range(len(x)):
        res[i]=depths[0][i]
    return res
    
    
    

simplicialVolume.__doc__="""

Description
    Calculates the simpicial volume depth of points w.r.t. a multivariate data set.

Usage
    depth.simplicialVolume(x, data, exact = F, k = 0.05, mah.estimate = "moment", mah.parMcd = 0.75, seed = 0)

Arguments
    x 			
            Matrix of objects (numerical vector as one object) whose depth is to be calculated;
            each row contains a d-variate point. Should have the same dimension as data.

    data 			
            Matrix of data where each row contains a d-variate point, w.r.t. which the depth is to be calculated.

    exact			
            ``exact=True`` (by default) implies the **exact algorithm**, ``exact=False`` implies the **approximative algorithm**, considering k simplices.

    k			
            |	**Number (k > 1)** or **portion (if 0 < k < 1)** of simplices that are considered if ``exact = F``. 
            |	If ``k > 1``, then the algorithmic complexity is polynomial in d but is independent of the number of observations in data, given k. 
            |	If ``0 < k < 1``, then the algorithmic complexity is exponential in the number of observations in data, but the calculation precision stays approximately the same.

    mah.estimate 		
            A character string specifying affine-invariance adjustment; can be ``none``, ``moment``
            or ``MCD``, determining whether no affine-invariance adjustemt or moment or Minimum Covariance Determinant (MCD) 
            (see covMcd) estimates of the covariance are used. By default ``moment`` is used.

    mah.parMcd 		
            The value of the argument alpha for the function covMcd is used when, ``mah.estimate = MCD``.


    seed 			
            The random seed. The default value **seed=0** makes no changes.

Examples
            >>> import numpy as np
            >>> from depth.multivariate import *
            >>> mat1=[[1, 0, 0],[0, 2, 0],[0, 0, 1]]
            >>> mat2=[[1, 0, 0],[0, 1, 0],[0, 0, 1]]
            >>> x = np.random.multivariate_normal([1,1,1], mat2, 10)
            >>> data = np.random.multivariate_normal([0,0,0], mat1, 20)
            >>> simplicalVolume(x, data, exact=True)
            [0.45749049 0.34956166 0.2263421  0.68742137 0.94796538 0.51112415
             0.85250931 0.67914988 0.79165292 0.33192247]
            >>> simplicalVolume(x, data, exact=False, k=0.2)
            [0.46826813 0.40138917 0.23189724 0.69025277 0.938543   0.56005713
             0.8113647  0.72220103 0.82036139 0.33908597]
"""

