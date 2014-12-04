from math import tanh, atanh
from scipy.stats import norm

# http://seriousstats.wordpress.com/2012/02/05/comparing-correlations/

def rz_ci(r, n, conf_level=0.95):
    ze = 1.0 / ((n-3.0)**0.5)
    moe = norm.ppf(1.0 - ((1.0-conf_level)/2.0)) * ze
    zu = atanh(r) + moe
    z1 = atanh(r) - moe
    return (tanh(z1), tanh(zu))

def rho_rxy_rxz(rxy, rxz, ryz):    
	num = (ryz-1.0/2.0*rxy*rxz)*(1.0-rxy**2-rxz**2-ryz**2)+ryz**3
	den = (1.0 - rxy**2) * (1 - rxz**2)
	return num / den

def r_doi_ci(r12, r13, r23, n, conf_level=0.95):    
    L1, U1 = rz_ci(r12, n, conf_level=conf_level)    
    L2, U2 = rz_ci(r13, n, conf_level=conf_level)
    rho_r12_r13 = rho_rxy_rxz(r12, r13, r23)    
    lower = r12-r13-((r12-L1)**2+(U2-r13)**2-2*rho_r12_r13*(r12-L1)*(U2- r13))**0.5
    upper = r12-r13+((U1-r12)**2+(r13-L2)**2-2*rho_r12_r13*(U1-r12)*(r13-L2))**0.5
    return (lower, upper) 

if __name__ == '__main__':

    #print r_doi_ci(.396, .179, .088, 66)
    print r_doi_ci(0.79918117418267931, 0.79966273252772757, 0.87211099335408615, 90)
