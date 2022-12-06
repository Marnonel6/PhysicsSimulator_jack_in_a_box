# PhysicsSimulator_jack_in_a_box
Machine Dynamics Final Project

[Screencast from 12-01-2022 06:48:27 PM.webm](https://user-images.githubusercontent.com/60977336/205214226-b14207b7-afa2-44e5-856c-bc6335cf23ab.webm)

The project guidelines are below.

`You should include a brief description of what you originally proposed and what changes you needed to make to your original proposal (and why you made them).If you chose the default project, you can simply state that you did so.`

A physics simulator was programmed in Python for a jack in a rotating box.

`You should include a drawing of the system you are modeling that includes all the frames you are using, with frame labels. In addition to the drawing, you should include all of the rigid body transformations you are using between the frames. These frames and their labels should be clearly identifiable in your code.`

![frames](https://user-images.githubusercontent.com/60977336/205214428-5d44d9da-ca58-4e47-ba6a-1420a1509ee1.jpg)

# Rigid body transformations:
`Jack and Box relative to world:`
g_w_b - Center Box relative to world
g_w_j - Center Jack relative to world

`Box:`
g_b_b1 - Right box wall relative to box center
g_b_b3 - Left box wall relative to box center
g_b_b2 - Lower box wall relative to box center
g_b_b4 - Lower box wall relative to box center

`Jack:`
g_j_j1 - Right jack corner relative to jack center
g_j_j3 - Left jack corner relative to jack center
g_j_j2 - Lower jack corner relative to jack center
g_j_j4 - Lower jack corner relative to jack center

`Reassign:`
g_wb = g_w_b
g_wj = g_w_j

`Each box wall relative to the world frame:`
g_wb1, g_wb2, g_wb3, g_wb4

`Each jack corner relative to the world frame:`
g_wj1, g_wj2, g_wj3, g_wj4


`Using the drawing and the rigid body transformations, you should say in writing how you calculate the Euler-Lagrange equations, the constraints, the external forces and impact update laws.`

`Euler-Lagrange equations:`
Calculated the rigid body transformations between the box and jack frame (g_wb, g_wj) respectively relative to the world frame.
Used the calculated transformations to calculate the body velocity of the jack and the box.
Calculated the inertia of the jack as four point masses and the box as four bars.
Then the inertia tensor, kinetic & potential energy, Lagrangian and the Euler Lagrangian was calculated.

`Constraints:`
The rigid body transformations where calculated between each wall and the four point masses of the jack.
This provided the 16 impact conditions that where possible in the simulation. The left/(3) and right/(1) wall of
the box is in the x-axis and thus the x translation value was extracted from the rigid body transformations
for wall as the constraint.
- phi_b1_j1 = (g_b1j1[0,3].subs(dummy_var)): Displays the impact condition between wall 1 and corner/point
mass 1 of the jack in the x-coordinate.
The lower/(2) and upper/(4) wall of the box is in the y-axis and thus the y 
translation value was extracted from the rigid body transformations as the constraint.
- phi_b2_j1 = (g_b2j1[1,3].subs(dummy_var)): Displays the impact condition between wall 2 and corner/point
mass 1 of the jack in the y-coordinate.

`External forces:`
A force in the y-axis was applied to the box to offset gravity and keep the box at a relatively constant y.
The value of the force is equal to the weight of the box plus 100[N] to negate the effects of the jack 
impacting with the box. This addition value was obtained through experimentation.
A torque was applied to the box to rotate the box and make the jack bounce around. The torque is a sine wave
with an amplitude equal to 80% the weight of the box.

`Impact update laws:`
if (phi_val[i] > -threshold) and (phi_val[i] < threshold): This checks if the impact condition's sign is changing
and if the sign changes then an impact occurred. This returns the impact index of between which wall and corner of
the jack the impact occurred. The impact update function is them called with the specific impact equation. The
initial or tau^- conditions is then substituted into the impact equations. The impact equations are then solved for
the tau^+ instance. Lambda is then checked and when lambda is very small the solution is considered as false and the
next solution is considered. When the lambda is not small that solution is then passed back as the new parameters at
tau^+.

`If your code works, you should describe in words what happens in the simulation and why you think it is correct (e.g., at a high level, describe why you think the behavior is reasonable or not). If your code works, this can be the end of your write-up. If your code works, your entire write-up will likely just be a few paragraphs.`

The jack is started at a angle when dropped. It then impacts with the box while the box rotates counter-clockwise.
The jack bounces off at an angle as the box has already started to rotate before the jack impacts with the box.
The jacks bounce angles seems correct considering the angle of the box. The jack also starts to rotate after impact
as the jack was dropped at angle relative to the horizontal axis. The rotation is slow as the angle is small. The 
jack then goes on to impact with the box in a reasonable manner, where when the box starts to rotate faster then the
impact has more energy and the jack bounces off with more energy and start spinning faster when the jack impacts in the
correct orientation.



