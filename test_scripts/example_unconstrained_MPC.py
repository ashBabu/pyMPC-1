import numpy as np
import scipy as sp
import scipy.linalg

if __name__ == '__main__':

    Ac = np.array([[1,2],
                  [3,4]], dtype = np.float)

    Bc = np.array([[1, 2],[2, 1]])
    [nx, nu] = Bc.shape # number of states and number or inputs
    [nx1, nx2] = Ac.shape

    Qx = np.diag([2,2])
    QxN = 2*Qx
    Qu = np.eye(nu)
    QDu = np.eye(nu)


    assert(nx1 == nx2)
    assert(nx1 == nx)

    Np = 4

    x0 = np.array([1,0])
    x0 = x0.reshape(-1,1)
    xref = np.ones(nx)
    Xref = np.kron(np.ones((Np,1)), xref.reshape(-1,1))

    uref = np.ones(nu)
    Uref = np.kron(np.ones((Np,1)), uref.reshape(-1,1))

    uminus1 = np.ones(nu)
    uminus1 = uminus1.reshape(-1,1)

    A_cal = np.empty((Np*nx, nx))
    B_cal = np.zeros((Np*nx, Np*nu))

    for k in range(0, Np):
        if k==0:
            A_km1 = np.eye(nx)
        else:
            A_km1 = A_cal[(k - 1) * nx:(k) * nx, 0:nx]
        A_cal[k * nx:(k + 1) * nx, 0:nx] = Ac @ A_km1

    for k in range(Np):
        if k == 0:
            A_k = np.eye(nx)
        else:
            A_k = A_cal[(k - 1) * nx:(k) * nx, 0:nx]
        A_kB = A_k @ Bc
        for p in range(Np-k):
            B_cal[(k+p)*nx:(k+p+1)*nx, p*nu:(p+1)*nu] = A_kB


    Q_cal_x = scipy.linalg.block_diag(np.kron(np.eye(Np-1), Qx),   # x0...x_N-1
                                      QxN)                              # xN
    Q_cal_u = scipy.linalg.block_diag(np.kron(np.eye(Np), Qu))   # x0...x_N-1

    iDu = 2 * np.eye(Np) - np.eye(Np, k=1) - np.eye(Np, k=-1)
    iDu[Np - 1, Np - 1] = 1
    Q_cal_Du = np.kron(iDu, QDu)


    P = np.transpose(B_cal) @ Q_cal_x @ B_cal
    P_inv = np.linalg.inv(P)
    p_ubar = np.vstack([-QDu,  # u0
                      np.zeros(((Np - 1)*nu, nu))])  # u1..uN-1

    p_x0 = np.transpose(B_cal) @ Q_cal_x @ A_cal
    p_Xref = -np.transpose(B_cal) @ Q_cal_x
    p_Uref = - Q_cal_u

    k_x0 = - P_inv @ p_x0
    k_Xref = -P_inv @ p_Xref
    k_ubar = -P_inv @ p_ubar
    k_Uref = -P_inv @ p_Uref

    p_tot = p_x0 @ x0 + p_Xref @ Xref + p_ubar @ uminus1 + p_Uref @ Uref

    u_MPC_all = -np.linalg.solve(P,p_tot)

    u_MPC_all = u_MPC_all.reshape(-1,nu)
    u_MPC = u_MPC_all[0,:]

    #u_MPC_all_2 = k_x0 @ x0 + k_Xref @ Xref + k_Uref @ Uref + k_ubar @ uminus1
