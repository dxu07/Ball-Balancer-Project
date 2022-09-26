'''!
    @file       main.py
    
    @brief      The main script for running the tasks of the final lab project.
    
    @details    The purpose of this main script is to run the tasks 
                responsible for the functionality of the final project.
                The shares/queues that will be used in this lab are also 
                primarily defined in this script.

                
    @author     Jake Lesher
    @author     Daniel Xu
    @date       02/16/2022
'''

import taskUser, taskIMU, taskMotor, taskController, taskPanel, shares

##  @brief      The variable, zFlag, is a shared variable
#   @details    This shared variable is a boolean that is shared between 
#               taskUser and taskEncoder to determine whether or not the 
#               encoder object needs to be zeroed.
#  
zFlag = shares.Share(False)

##  @brief      The variable, Data, is a queue of shared data.
#   @details    This shared queue is the positional data of the encoder, in 
#               radians. It is updated in taskEncoder and recorded in taskUser.
#  
Data = shares.Share()

##  @brief      The variable, Delta, is a queue of shared data.
#   @details    This shared queue is the delta data of the encoder in radians.
#               It is updated in taskEncoder and recorded in taskUser.
#  
Delta = shares.Share()

##  @brief      The variable, Velocity, is a queue of shared data.
#   @details    This shared queue is the current angular velocity in rad/s.
#               It is updated in taskEncoder and recorded in taskUser.
#
Velocity = shares.Share()

##  @brief      The variable, Duty1, is a queue of shared data.
#   @details    This shared queue is the duty cycle for motor 1 as requested
#               in taskUser. The queue is then read in taskMotor, where it is
#               sent to the motor driver.
#
Duty1 = shares.Share()

##  @brief      The variable, Duty2, is a queue of shared data.
#   @details    This shared queue is the current angular velocity in rad/s.
#               It is updated in taskEncoder and recorded in taskUser.
#
Duty2 = shares.Share()

##  @brief      The variable, clFlag, is a shared variable
#   @details    This shared variable is a boolean that is shared between 
#               taskUser and taskController to determine whether or not the 
#               motor should be running in closed-loop.
#  
clFlag = shares.Share(False)

##  @brief      The variable, Kp, is a shared variable
#   @details    This shared variable is the value of the proportional gain to 
#               be used in the closed-loop.
#  
Kp = shares.Share()

##  @brief      The variable, Ki, is a shared variable
#   @details    This shared variable is the value of the integral gain to 
#               be used in the closed-loop.
#  
Ki = shares.Share()

##  @brief      The variable, Kd, is a shared variable
#   @details    This shared variable is the value of the derivative gain to 
#               be used in the closed-loop.
#  
Kd = shares.Share()

##  @brief      The variable, AngVel, is a shared variable
#   @details    This shared variable is the value of __________
#
#  
AngVel = shares.Share()

##  @brief      The variable, Position, is a shared variable
#   @details    This shared variable is the value position read by the touch
#               panel [mm].
#  
Position = shares.Share()

##  @brief      The variable, Contact, is a shared variable
#   @details    This shared variable is a boolean telling if there is z-contact
#               on the touch panel.
#  
Contact = shares.Share()

if __name__ == '__main__':
    
    # taskList will be the list used to define the three tasks that will run
    # sequentially in 10 ms intervals.
    taskList = [taskIMU.taskIMUFcn('taskIMU', 10_000, Data, Velocity),
                taskPanel.taskPanelFcn('taskPanel', 10_000, Position, Contact),
                taskUser.taskUserFcn('taskUser', 10_000, Data, Velocity, Duty1, Duty2, clFlag, Kp, Ki,Kd, Position, Contact),
                taskMotor.taskMotorFcn('taskMotor', 10_000, Duty1, Duty2),
                taskController.taskControllerFcn('taskController', 10_000, clFlag, Velocity, Duty1, Kp, Ki, Kd, Data, Duty2, Position, Contact)]
    
    # taskList = [taskPanel.taskPanelFcn('taskPanel', 10_000, Position, Contact)]
    
    while True:
        
        # With this loop we want to look for a keyboard interrupt (Ctrl+C).
        # It will try to run the code until Ctrl+C happens and then break.
        try:
            for task in taskList:
                next(task)
            
        except KeyboardInterrupt:
            # A KeyboardInterrupt is ctrl+C in the terminal.
            break
        
    print("Program Terminating")