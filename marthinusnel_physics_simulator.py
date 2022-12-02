# -*- coding: utf-8 -*-
"""MarthinusNel_Physics_Simulator.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FK1vUKFzGPrOcCbqbbMhauiCZXAcmSrM

# Marthinus Nel ME314 Final Project

###Submission details

## Imports
"""

import sympy as sym
import numpy as np
from math import pi
import matplotlib.pyplot as plt

##############################################################################################
#Run it before you start programming, this will enable the nice 
# LaTeX "display()" function for you. If you're using the local Jupyter environment
##############################################################################################
def custom_latex_printer(exp,**options):
    from google.colab.output._publish import javascript
    url = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.1.1/latest.js?config=TeX-AMS_HTML"
    javascript(url=url)
    return sym.printing.latex(exp,**options)
sym.init_printing(use_latex="mathjax",latex_printer=custom_latex_printer)

"""## Helper Functions"""

def SE3_unhat(V):
    return sym.Matrix([[V[0,3]], [V[1,3]], [V[2,3]], [V[2,1]], [V[0,2]], [V[1,0]]])

def transformationMatrix_sym(theta, p):
    """Converts theta and translation 3 vector into a 4x4 matrix in se3

    :param: theta and translation p (3 vector)
    :return: The 4x4 se3 representation of theta and p (translation)
    """
    
    return sym.Matrix([[sym.cos(theta), -sym.sin(theta), 0, p[0]],
                       [sym.sin(theta),  sym.cos(theta), 0, p[1]],
                       [             0,               0, 1, p[2]],
                       [             0,               0, 0,    1]])
    
def transformationMatrix_numpy(theta, p):
    """Converts theta and translation 3 vector into a 4x4 matrix in se3

    :param: theta and translation p (3 vector)
    :return: The 4x4 se3 representation of theta and p (translation)
    """
    
    return np.array([[np.cos(theta), -np.sin(theta), 0, p[0]],
                     [np.sin(theta),  np.cos(theta), 0, p[1]],
                     [           0,               0, 1, p[2]],
                     [           0,               0, 0,    1]])
    
def InvSE3(SE3):
    """
    Performs matrix inverse.
    
    :param SE3: SE3
    :return: SE3^-1 or SE3.T
    """
    R = sym.Matrix([[SE3[0,0], SE3[0,1], SE3[0,2]],
                    [SE3[1,0], SE3[1,1], SE3[1,2]],
                    [SE3[2,0], SE3[2,1], SE3[2,2]]])
    p = sym.Matrix([[SE3[0,3]],
                    [SE3[1,3]],
                    [SE3[2,3]]])

    R_T = R.T
    p_T = -R_T*p

    return sym.Matrix([[R_T[0,0], R_T[0,1], R_T[0,2], p_T[0]],
                       [R_T[1,0], R_T[1,1], R_T[1,2], p_T[1]],
                       [R_T[2,0], R_T[2,1], R_T[2,2], p_T[2]],
                       [       0,        0,        0,       1]])

def Vb(SE3):
    """
    inv(g)*diff(g)
    """
    return SE3_unhat(InvSE3(SE3)*SE3.diff(t))

def Inertia_mat_KE(m,J):
    return sym.Matrix([[m, 0, 0, 0, 0, 0],
                       [0, m, 0, 0, 0, 0],
                       [0, 0, m, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, 0],
                       [0, 0, 0, 0, 0, J]])

"""## Functions for simulation"""

def plot(traj, tspan, dt):
  """Plot box and jack motion."""
  x_t = np.linspace(tspan[0], tspan[1], int(tspan[1]/dt))
  plt.figure()
  plt.plot(x_t, traj[0], label=r'$x_b(t)$')
  plt.plot(x_t, traj[1], label=r'$y_b(t)$')
  plt.plot(x_t, traj[2], label=r'$\theta_b(t)$')
  plt.title('Box $x_b$, $y_b$ and $theta_b$ vs Time [t]')
  plt.xlabel('t')
  plt.legend(loc='upper left')
  plt.show()
  plt.figure()
  plt.plot(x_t, traj[3], label=r'$x_j(t)$')
  plt.plot(x_t, traj[4], label=r'$y_j(t)$')
  plt.plot(x_t, traj[5], label=r'$\theta_j(t)$')
  plt.title('Dice $x_j$, $y_j$ and $theta_j$ vs Time [t]')
  plt.xlabel('t')
  plt.legend(loc='lower left')
  plt.show()

def integrate(f, xt, dt, t):
  """
  RK4 integration
  """
  k1 = dt * f(xt, t)
  k2 = dt * f(xt+k1/2., t/2) # t+dt/2
  k3 = dt * f(xt+k2/2., t/2) # t+dt/2
  k4 = dt * f(xt+k3, t)
  new_xt = xt + (1/6.) * (k1+2.0*k2+2.0*k3+k4)

  return new_xt

def impact_update(s, impact_EQ, dummy_p):
  """Function to update the system upon impact."""
  # Sub in new ICs
  impact_eqns_update = impact_EQ.subs({xb:s[0], yb:s[1], thetab:s[2], xj:s[3], 
                                      yj:s[4], thetaj:s[5], dxb:s[6], dyb:s[7], 
                                      dthetab:s[8], dxj:s[9], dyj:s[10],
                                      dthetaj:s[11]})
  display(impact_eqns_update)
  solns = sym.solve(impact_eqns_update, [dxb_p, dyb_p, dthetab_p, dxj_p,
                                             dyj_p, dthetaj_p, lamb], dict=True)
  if len(solns) == 1:
      pass
  else:
      for sol in solns:
          solns_lamb = sol[lamb]
          if abs(solns_lamb) < 1e-06:
              pass # False solution
          else:
              return np.array([s[0], s[1], s[2], s[3], s[4], s[5],
                               float(sol[dummy_p[0]]), float(sol[dummy_p[1]]),
                               float(sol[dummy_p[2]]), float(sol[dummy_p[3]]),
                               float(sol[dummy_p[4]]), float(sol[dummy_p[5]])])

def impact_condition(s, threshold=1e-1):
  """Check for impact."""
  phi_val = phi_f(*s)
  for i in range(phi_val.shape[0]):
      if (phi_val[i] > -threshold) and (phi_val[i] < threshold):
          return (True, i)
  return (False, None)

def simulate_with_impact(f, x0 , tspan , dt , integrate):
  t = 0 # Initialize time
  N = int((max(tspan)-min(tspan))/dt)
  x = np.copy(x0)
  tvec = np.linspace(min(tspan), max(tspan), N)
  xtraj = np.zeros((len(x0), N))
  for i in range (N):
      t = t + dt # Increment time with timestep dt
      (impact_occured, impact_num) = impact_condition(x)
      if impact_occured is True:
          x = impact_update(x, impact_EQ[impact_num], dummy_p)
          xtraj[:,i]=integrate(f, x, dt, t)
      else :
          xtraj[:,i]=integrate(f, x, dt, t)
      x = np.copy(xtraj[:,i])
  return xtraj

def dyn(s, t):
  "Dynamics."
  return np.array([s[6], s[7], s[8], s[9], s[10], s[11], ddx_b_f(*s, t), 
                  ddy_b_f(*s, t), ddtheta_b_f(*s, t), ddx_j_f(*s, t),
                  ddy_j_f(*s, t), ddtheta_j_f(*s, t)])

"""## Variables, Forces and State variables"""

# Define variables
t, lamb = sym.symbols(r't, \lambda')

# Configuration variables
x_b = sym.Function(r"x_b")(t)
y_b = sym.Function(r"y_b")(t)
theta_b = sym.Function(r"\theta_b")(t)

x_j = sym.Function(r"x_j")(t)
y_j = sym.Function(r"y_j")(t)
theta_j= sym.Function(r"\theta_j")(t)

# State variable
q = sym.Matrix([x_b, y_b, theta_b, x_j, y_j, theta_j])
dq = q.diff(t)
ddq = dq.diff(t)

# Define box parameters
l_b = 10
m_b = 1000
J_b = m_b*(1/12*(l_b**2)) 

# Define dice parameters
l_j = 1
m_j = 5 
J_j = 4*(m_j*(0.70711)**2) 

# Gravity
g = 9.81

# Forces
# To counteract gravity pulling the box down. This is the same as the box being 
# fixed in space in the y-axis
F_y_b = m_b*g + 100 # Had to add more force to stop the box from moving down
F_theta_b = (m_b*9.81*sym.sin(pi*t/4))*0.8
F_mat = sym.Matrix([0, F_y_b, F_theta_b, 0, 0, 0])

"""## Transformation Matrices"""

######## Dice and Box center ########
# Center Box relative to world
g_w_b = transformationMatrix_sym(theta_b, [x_b,y_b,0])
# Center Jack/Dice relative to world
g_w_j = transformationMatrix_sym(theta_j, [x_j,y_j,0])

######## Box walls ########
# Right box wall relative to box center
g_b_b1 = transformationMatrix_sym(0, [l_b/2,0,0])
# Left box wall relative to box center
g_b_b3 = transformationMatrix_sym(0, [-l_b/2,0,0])
# Lower box wall relative to box center
g_b_b2 = transformationMatrix_sym(0, [0,-l_b/2,0])
# Lower box wall relative to box center
g_b_b4 = transformationMatrix_sym(0, [0,l_b/2,0])

######## Jack/Dice corners ########
# Right dice corner relative to dice center
g_j_j1 = transformationMatrix_sym(0, [l_j/2,l_j/2,0])
# Left dice corner relative to dice center
g_j_j3 = transformationMatrix_sym(0, [-l_j/2,-l_j/2,0])
# Lower dice corner relative to dice center
g_j_j2 = transformationMatrix_sym(0, [l_j/2,-l_j/2,0])
# Lower dice corner relative to dice center
g_j_j4 = transformationMatrix_sym(0, [-l_j/2,l_j/2,0])

######## Generate desired Transformation matrices ########
g_wb = g_w_b
g_wj = g_w_j
# Each box wall relative to the world frame
g_wb1 = g_w_b@g_b_b1
g_wb2 = g_w_b@g_b_b2
g_wb3 = g_w_b@g_b_b3
g_wb4 = g_w_b@g_b_b4
# Each dice corner relative to the world frame
g_wj1 = g_w_j@g_j_j1
g_wj2 = g_w_j@g_j_j2
g_wj3 = g_w_j@g_j_j3
g_wj4 = g_w_j@g_j_j4

# Each box side relative to each dice corner
g_b1j1 = InvSE3(g_wb1)@g_wj1
g_b1j2 = InvSE3(g_wb1)@g_wj2
g_b1j3 = InvSE3(g_wb1)@g_wj3
g_b1j4 = InvSE3(g_wb1)@g_wj4
g_b2j1 = InvSE3(g_wb2)@g_wj1
g_b2j2 = InvSE3(g_wb2)@g_wj2
g_b2j3 = InvSE3(g_wb2)@g_wj3
g_b2j4 = InvSE3(g_wb2)@g_wj4
g_b3j1 = InvSE3(g_wb3)@g_wj1
g_b3j2 = InvSE3(g_wb3)@g_wj2
g_b3j3 = InvSE3(g_wb3)@g_wj3
g_b3j4 = InvSE3(g_wb3)@g_wj4
g_b4j1 = InvSE3(g_wb4)@g_wj1
g_b4j2 = InvSE3(g_wb4)@g_wj2
g_b4j3 = InvSE3(g_wb4)@g_wj3
g_b4j4 = InvSE3(g_wb4)@g_wj4

"""## Lagrangian"""

# Velocity of box and jack
V_b = Vb(g_wb)
V_j = Vb(g_wj)

# Inertia Matrix for box and jack
I_b = Inertia_mat_KE(m_b,J_b)
I_j = Inertia_mat_KE(m_j,J_j)

# Kinetic Energy
KE = sym.simplify((0.5*(V_b.T)*I_b*V_b + 0.5*(V_j.T)*I_j*V_j)[0])

# Potential Energy
V = sym.simplify(g*m_b*y_b + g*m_j*y_j)

# Lagrangian
L = sym.simplify(KE - V)
print("\n\033[1m Lagrangian: ")
display(L)

# Jacobian with respect to the state
dldq = sym.simplify(sym.Matrix([L]).jacobian(q).T)
# Jacobian with respect to the state derivative
dldqd = sym.simplify(sym.Matrix([L]).jacobian(dq).T)

# Eular Lagrangian/ Left hand side
EL = sym.simplify(dldqd.diff(t) - dldq)
lhs = EL
# define right hand side as a Matrix
rhs = F_mat

# Define the equations
EL_eqn = sym.Eq(lhs, rhs)
print('\n\033[1m EL_eqn:')
display(EL_eqn)

# solve Euler Lagrange equations
solns = sym.solve(EL_eqn, ddq, dict=True)

# ddot solutions
for sol in solns:
    print('\n\033[1m Solution: ')
    for v in ddq:
        display(sym.Eq(v, sol[v]))

"""## Lamdify variables"""

# Lamdify double derivatives
ddx_b_f = sym.lambdify([*q, *dq, t], solns[0][ddq[0]])
ddy_b_f = sym.lambdify([*q, *dq, t], solns[0][ddq[1]])
ddtheta_b_f = sym.lambdify([*q, *dq, t], solns[0][ddq[2]])
ddx_j_f = sym.lambdify([*q, *dq, t], solns[0][ddq[3]])
ddy_j_f = sym.lambdify([*q, *dq, t], solns[0][ddq[4]])
ddtheta_j_f = sym.lambdify([*q, *dq, t], solns[0][ddq[5]])

"""## Dummy Variables"""

xb, yb, thetab, xj, yj, thetaj = sym.symbols(r'x_b, y_b, \theta_b, x_j, y_j, \theta_j')
dxb, dyb, dthetab, dxj, dyj, dthetaj = sym.symbols(r'\dot{x_b}, \dot{y_b}, \dot{\theta_b}, \dot{x_j}, \dot{y_j}, \dot{\theta_j}')

dummy_var = {q[0]:xb, q[1]:yb, q[2]:thetab,
              q[3]:xj, q[4]:yj, q[5]:thetaj,
              dq[0]:dxb, dq[1]:dyb, dq[2]:dthetab,
              dq[3]:dxj, dq[4]:dyj, dq[5]:dthetaj}

dxb_p, dyb_p, dthetab_p, dxj_p, dyj_p, dthetaj_p = sym.symbols(r'\dot{x_b}^+, \dot{y_b}^+, \dot{\theta_b}^+, \dot{x_j}^+, \dot{y_j}^+, \dot{\theta_j}^+')

dummy_after_impact = {dxb:dxb_p, dyb:dyb_p, dthetab:dthetab_p,
               dxj:dxj_p, dyj:dyj_p, dthetaj:dthetaj_p}

dummy_p = [dxb_p, dyb_p, dthetab_p,
               dxj_p, dyj_p, dthetaj_p]

"""## Constraints / Impact conditions"""

# Define impact constraints
# Wall 1 - Check x-value
phi_b1_j1 = (g_b1j1[0,3].subs(dummy_var))
phi_b1_j2 = (g_b1j2[0,3].subs(dummy_var))
phi_b1_j3 = (g_b1j3[0,3].subs(dummy_var))
phi_b1_j4 = (g_b1j4[0,3].subs(dummy_var))
# Wall 2 - Check y-value
phi_b2_j1 = (g_b2j1[1,3].subs(dummy_var))
phi_b2_j2 = (g_b2j2[1,3].subs(dummy_var))
phi_b2_j3 = (g_b2j3[1,3].subs(dummy_var))
phi_b2_j4 = (g_b2j4[1,3].subs(dummy_var))
# Wall 3 - Check x-value
phi_b3_j1 = (g_b3j1[0,3].subs(dummy_var))
phi_b3_j2 = (g_b3j2[0,3].subs(dummy_var))
phi_b3_j3 = (g_b3j3[0,3].subs(dummy_var))
phi_b3_j4 = (g_b3j4[0,3].subs(dummy_var))
# Wall 4 - Check y-value
phi_b4_j1 = (g_b4j1[1,3].subs(dummy_var))
phi_b4_j2 = (g_b4j2[1,3].subs(dummy_var))
phi_b4_j3 = (g_b4j3[1,3].subs(dummy_var))
phi_b4_j4 = (g_b4j4[1,3].subs(dummy_var))

# total impact constraint
phi = sym.Matrix([[phi_b1_j1], [phi_b1_j2], [phi_b1_j3], [phi_b1_j4],
                  [phi_b2_j1], [phi_b2_j2], [phi_b2_j3], [phi_b2_j4],
                  [phi_b3_j1], [phi_b3_j2], [phi_b3_j3], [phi_b3_j4],
                  [phi_b4_j1], [phi_b4_j2], [phi_b4_j3], [phi_b4_j4]])

# Lamdify
phi_f = sym.lambdify([xb, yb, thetab, xj, yj, thetaj, dxb, dyb, dthetab, dxj, 
                      dyj, dthetaj], phi)

"""## Hamiltonion and Impact eqns"""

# Hamiltonion
print('\n\033[1m Hamiltonion: ')
H = sym.simplify((dldqd.T * dq)[0] - L)
H_subs = H.subs(dummy_var)
display(H_subs)
dldqd_subs = dldqd.subs(dummy_var)
dphidq = phi.jacobian([xb, yb, thetab, xj, yj, thetaj])

# Hamiltonion Plus
print('\n\033[1m Hamiltonion Plus: ')
H_p = sym.simplify(H_subs.subs(dummy_after_impact))
display(H_p)
dldqd_p = sym.simplify(dldqd_subs.subs(dummy_after_impact))
dphidq_p = sym.simplify(dphidq.subs(dummy_after_impact))

lhs = sym.simplify(sym.Matrix([dldqd_p[0] - dldqd_subs[0], 
                               dldqd_p[1] - dldqd_subs[1],
                               dldqd_p[2] - dldqd_subs[2], 
                               dldqd_p[3] - dldqd_subs[3],
                               dldqd_p[4] - dldqd_subs[4],
                               dldqd_p[5] - dldqd_subs[5],
                               H_p - H_subs]))
impact_EQ = []
for i in range(phi.shape[0]):
    rhs = sym.Matrix([lamb * dphidq[i, 0], lamb*dphidq[i, 1],
                      lamb*dphidq[i, 2], lamb*dphidq[i, 3],
                      lamb*dphidq[i, 4], lamb*dphidq[i, 5],
                      0])
    impact_EQ.append(sym.Eq(lhs, rhs))

"""## Simulation"""

# Simulation constants
tspan = [0, 7]
dt = 0.01
s0 = np.array([0, 0, 0, 0, 2, -pi/3, 0, 0, 0, 0, 0, 0])

traj = simulate_with_impact(dyn, s0, tspan, dt, integrate)
print('\033[1m Shape of traj:', traj.shape)

"""## Plot Graphs"""

# Plot
plot(traj, tspan, dt)

def animate_jack_in_box(theta_array, L_box, L_jack, T):
    """
    Function to generate web-based animation of a jack in a box

    Parameters:
    ================================================
    theta_array:
        trajectory of xb, yb, thetab, xj, yj, thetaj
    L_box:
        length of the box
    L_jack:
        length of the jack
    T:
        length/seconds of animation duration

    Returns: None
    """

    ################################
    # Imports required for animation.
    from plotly.offline import init_notebook_mode, iplot
    from IPython.display import display, HTML
    import plotly.graph_objects as go

    #######################
    # Browser configuration.
    def configure_plotly_browser_state():
        import IPython
        display(IPython.core.display.HTML('''
            <script src="/static/components/requirejs/require.js"></script>
            <script>
              requirejs.config({
                paths: {
                  base: '/static/base',
                  plotly: 'https://cdn.plot.ly/plotly-1.5.1.min.js?noext',
                },
              });
            </script>
            '''))
    configure_plotly_browser_state()
    init_notebook_mode(connected=False)

    ###############################################
    # Getting data from trajectories.
    N = len(theta_array[0]) 
    xb_array = theta_array[0]
    yb_array = theta_array[1]
    thetab_array = theta_array[2]
    xj_array = theta_array[3]
    yj_array = theta_array[4]
    thetaj_array = theta_array[5]

    ###############################################
    # Define arrays containing data for frame axes
    # Box
    frame_b1_x = np.zeros(N)
    frame_b1_y = np.zeros(N)
    frame_b2_x = np.zeros(N)
    frame_b2_y = np.zeros(N)
    frame_b3_x = np.zeros(N)
    frame_b3_y = np.zeros(N)
    frame_b4_x = np.zeros(N)
    frame_b4_y = np.zeros(N)
    # Jack
    frame_j1_x = np.zeros(N)
    frame_j1_y = np.zeros(N)
    frame_j2_x = np.zeros(N)
    frame_j2_y = np.zeros(N)
    frame_j3_x = np.zeros(N)
    frame_j3_y = np.zeros(N)
    frame_j4_x = np.zeros(N)
    frame_j4_y = np.zeros(N)
    
    for i in range(N): # iteration through each time step
        g_wb = transformationMatrix_numpy(thetab_array[i], [xb_array[i], yb_array[i], 0])
        g_wj = transformationMatrix_numpy(thetaj_array[i], [xj_array[i], yj_array[i], 0])
        # Box
        frame_b1_x[i] = (g_wb.dot(([L_box/2, L_box/2, 0, 1])))[0]
        frame_b1_y[i] = (g_wb.dot(([L_box/2, L_box/2, 0, 1])))[1]
        frame_b2_x[i] = (g_wb.dot(([L_box/2, -L_box/2, 0, 1])))[0]
        frame_b2_y[i] = (g_wb.dot(([L_box/2, -L_box/2, 0, 1])))[1]
        frame_b3_x[i] = (g_wb.dot(([-L_box/2, -L_box/2, 0, 1])))[0]
        frame_b3_y[i] = (g_wb.dot(([-L_box/2, -L_box/2, 0, 1])))[1]
        frame_b4_x[i] = (g_wb.dot(([-L_box/2, L_box/2, 0, 1])))[0]
        frame_b4_y[i] = (g_wb.dot(([-L_box/2, L_box/2, 0, 1])))[1]
        # Jack
        frame_j1_x[i] = (g_wj.dot(([L_jack/2, L_jack/2, 0, 1])))[0]
        frame_j1_y[i] = (g_wj.dot(([L_jack/2, L_jack/2, 0, 1])))[1]
        frame_j2_x[i] = (g_wj.dot(([L_jack/2, -L_jack/2, 0, 1])))[0]
        frame_j2_y[i] = (g_wj.dot(([L_jack/2, -L_jack/2, 0, 1])))[1]
        frame_j3_x[i] = (g_wj.dot(([-L_jack/2, -L_jack/2, 0, 1])))[0]
        frame_j3_y[i] = (g_wj.dot(([-L_jack/2, -L_jack/2, 0, 1])))[1]
        frame_j4_x[i] = (g_wj.dot(([-L_jack/2, L_jack/2, 0, 1])))[0]
        frame_j4_y[i] = (g_wj.dot(([-L_jack/2, L_jack/2, 0, 1])))[1]
    
    ####################################
    # Using these to specify axis limits.
    xm = -8
    xM = 8
    ym = -8
    yM = 8

    ###########################
    # Defining data dictionary.
    # Trajectories are here.
    data=[
        dict(name='Box'),
        dict(name='Jack'),
        dict(name='Jack massless rod'),
        dict(name='Jack massless rod'),
        ]

    ################################
    # Preparing simulation layout.
    # Title and axis ranges are here.
    layout=dict(autosize=False, width=1000, height=1000,
                xaxis=dict(range=[xm, xM], autorange=False, zeroline=False,dtick=1),
                yaxis=dict(range=[ym, yM], autorange=False, zeroline=False,scaleanchor = "x",dtick=1),
                title='Jack in a Box physics simulation.', 
                hovermode='closest',
                updatemenus= [{'type': 'buttons',
                               'buttons': [{'label': 'Simulate','method': 'animate',
                                            'args': [None, {'frame': {'duration': T, 'redraw': False}}]},
                                           {'args': [[None], {'frame': {'duration': T, 'redraw': False}, 'mode': 'immediate',
                                            'transition': {'duration': 0}}],'label': 'Stop','method': 'animate'}
                                          ]
                              }]
               )

    ########################################
    # Defining the frames of the simulation.
    frames=[dict(data=[
                      #################### BOX LINES ############################
                      dict(x=[frame_b1_x[k], frame_b2_x[k], frame_b3_x[k], frame_b4_x[k], frame_b1_x[k]], 
                           y=[frame_b1_y[k], frame_b2_y[k], frame_b3_y[k], frame_b4_y[k], frame_b1_y[k]], 
                           mode='lines',
                           line=dict(color='black', width=5),
                           ),
                      #################### JACK POINT MASSES ############################
                      go.Scatter(
                            x=[frame_j1_x[k], frame_j2_x[k], frame_j3_x[k], frame_j4_x[k], frame_j1_x[k]], 
                            y=[frame_j1_y[k], frame_j2_y[k], frame_j3_y[k], frame_j4_y[k], frame_j1_y[k]], 
                            mode="markers",
                            marker=dict(color="blue", size=8)),
                       #################### JACK POINT LINES ############################
                       dict(x=[frame_j1_x[k], frame_j3_x[k]],
                            y=[frame_j1_y[k], frame_j3_y[k]],
                            mode='lines',
                            line=dict(color='red', width=2),
                            ),
                       dict(x=[frame_j2_x[k], frame_j4_x[k]], 
                            y=[frame_j2_y[k], frame_j4_y[k]], 
                            mode='lines',
                            line=dict(color='red', width=2),
                            ),
                      ]) for k in range(N)]

    #######################################
    # Putting it all together and plotting.
    figure1=dict(data=data, layout=layout, frames=frames)        
    iplot(figure1)

# If everything is not showing up run this cell again
animate_jack_in_box(traj,L_box=l_b,L_jack=l_j,T=tspan[1])