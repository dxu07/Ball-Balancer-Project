'''!
    @file       taskController.py
    
    @brief      The task that interfaces with the Closed Loop class.
    
    @details    This task's main function is to provide the ClosedLoop driver
                with the user-selected gain and Vref values.

                
    @author     Jake Lesher
    @author     Daniel Xu
    @date       02/23/2022
'''

from time import ticks_us, ticks_add, ticks_diff
import pyb  
import micropython, motor, shares, ClosedLoop

# Defining states

# Initialization state
S0_INIT = micropython.const(0)
# Set duty cycle state
S1_SET = micropython.const(1)
# Clear the fault condition state
S2_ACTIVE = micropython.const(2)
# State where platform balances without a ball.
S3_NOBALL = micropython.const(3)


def taskControllerFcn(taskName, period, clFlag, Velocity, Duty1,Kp,Ki,Kd,Data,Duty2, Position, Contact):
    '''!@brief      This function interacts with the ClosedLoop driver, sending 
                    a duty cycle based on the calculated error.
        @details    This function calls upon the driver to set the duty cycle
                    percentage for motor 1.
        @param      taskName is the name associated the with taskController in 
                    main.py. 
        @param      period sets the rate at which taskController is to run.
        @param      clFlag is the shared boolean that toggles closed-loop control.
        @param      Velocity is the share of the velocity value with 
                    taskEncoder.py
        @param      Vref is the share of the velocity requested by the user in
                    taskUser.
        @param      Duty1 is the share that contains the duty cycle percentage
                    for motor 1.
        @param      Kp is the share of the user-requested proportional gain.
        @param      Ki is the share of the user-requested integral gain.
    '''
    
    # State 0 is used only for initialization, so it will not exist within 
    # the while loop.
    state = S0_INIT

    start_time = ticks_us()
    next_time = ticks_add(start_time, period)
    prev_time = start_time
    ClosedLoopControl_1 = ClosedLoop.ClosedLoop()
    ClosedLoopControl_2 = ClosedLoop.ClosedLoop()
    state = S1_SET
    Position.write((0,0))
    prev_x_pos = Position.read()[0]
    prev_y_pos = Position.read()[1]
    Kp.write((0.16, 11))
    Ki.write((.01, 0))
    Kd.write((0.02, 0.2))
    prev_theta_x_ref = 0
    prev_theta_y_ref = 0
    true_count = 0
    false_count = 0
 
    while True:
        current_time = ticks_us()
        if ticks_diff(current_time,next_time)>=0:
            next_time = ticks_add(next_time,period)
            
            # Disable 
            if state == S1_SET:
                Duty1.write(0)
                Duty2.write(0)
                if clFlag.read() == True:
                    state = S3_NOBALL
                if clFlag.read() == True and Contact.read() == True:
                    state = S2_ACTIVE
                
                else: 
                    yield None
            # Enable
            elif state == S2_ACTIVE:
                if Contact.read() == False:
                    false_count += 1
                if Contact.read() == True:
                    true_count +=1
                #print("Controller State 2: Active")
                ang_vel = Velocity.read() # In units of degrees/s.
                eul_ang = Data.read() # In units of degrees.
                
                ClosedLoopControl_1.set_gain_outer(Kp.read()[0], Ki.read()[0], Kd.read()[0])
                ClosedLoopControl_2.set_gain_outer(-1*Kp.read()[0], -1*Ki.read()[0], -1*Kd.read()[0])
                
                ClosedLoopControl_1.set_gain_inner(Kp.read()[1], Ki.read()[1], Kd.read()[1])
                ClosedLoopControl_2.set_gain_inner(Kp.read()[1], Ki.read()[1], Kd.read()[1])
                
                dt = ticks_diff(current_time, prev_time)/1000000
                
                x_ref = 0
                y_ref = 0
                
                x_pos = Position.read()[0]
                y_pos = Position.read()[1]
                
                    
                
                v_x = (x_pos - prev_x_pos)/dt
                v_y = (y_pos - prev_y_pos)/dt
                
                if true_count >= false_count:
                # Outer Loop

                    if Contact.read() == False:
                        theta_x_ref = prev_theta_x_ref
                        theta_y_ref = prev_theta_y_ref
                        
                    else:
                        theta_x_ref = ClosedLoopControl_2.update_outer(y_pos, dt, v_y, y_ref, Contact.read())
                        theta_y_ref = ClosedLoopControl_1.update_outer(x_pos, dt, v_x, x_ref, Contact.read())
                    prev_theta_x_ref = theta_x_ref
                    prev_theta_y_ref = theta_y_ref

                    
                if false_count > true_count:
                    
                    theta_x_ref = 0
                    theta_y_ref = 0
                count_diff = abs(false_count - true_count)
                if count_diff >= 10:
                    
                    if false_count > true_count:
                        false_count = 3
                        true_count = 0
                    elif true_count > false_count:
                        true_count = 3
                        false_count = 0
                        

                        
                
                #Inner Loop
                Duty2.write(ClosedLoopControl_2.update_inner(eul_ang[0], dt, ang_vel[0], theta_x_ref))
                Duty1.write(ClosedLoopControl_1.update_inner(eul_ang[1], dt, ang_vel[1], theta_y_ref))
                
                #print(Duty1.read(), Duty2.read(), theta_x_ref, theta_y_ref, Contact.read())
                
                prev_x_pos = x_pos
                prev_y_pos = y_pos
                # if Contact.read() == False:
                #     clFlag.write(False)
                    
                if clFlag.read() == False:
                    state = S1_SET
                else:
                    yield None
            
            elif state == S3_NOBALL:
               # print("Controller State 3: No Ball")
                ang_vel = Velocity.read() # In units of degrees/s.
                eul_ang = Data.read() # In units of degrees.
                
                ClosedLoopControl_1.set_gain_inner(4, 2, 0.2)
                ClosedLoopControl_2.set_gain_inner(4, 2, 0.2)
                
                dt = ticks_diff(current_time, prev_time)/1000000
                
                theta_x_ref = 0
                theta_y_ref = 0
                
                Duty2.write(ClosedLoopControl_2.update_inner(eul_ang[0], dt, ang_vel[0], theta_x_ref)) 
                Duty1.write(ClosedLoopControl_1.update_inner(eul_ang[1], dt, ang_vel[1], theta_y_ref))
                
                if Contact.read() == True:
                    state = S2_ACTIVE
                if clFlag.read() == False:
                    state = S1_SET
                    
            prev_time = current_time
                

            
        else:
            yield None