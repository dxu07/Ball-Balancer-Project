'''!
    @file       ClosedLoop.py
    
    @brief      Driver that calculates the duty cycle of motor to follow closed-loop 
                control.
    
    @details    This driver communicates mainly with taskController, which sends
                duty cycle values calculated using the error. 
    
                The source code can be found at my repository under "Final Lab":
                https://bitbucket.org/jakelesher/me-305-labs
                
    @author     Jake Lesher
    @author     Daniel Xu
    @date       03/10/2022
    
'''
import pyb

class ClosedLoop:
    '''!
        @brief      Contains all of the functions that are responsible
                    for closed-loop PID control.
        @details    This class is used to calculate a value based on a closed
                    loop PID controller architecture. This calculated value can
                    be anything, as long as the correct inputs are given, 
                    making this driver very reusable. Separate functions were
                    used for the inner and outer control loops to easily 
                    differentiate the variables from each other.
                    
    '''
    def __init__(self):
        '''!@brief      A function that initializes the controller driver.
            @details    This fucntion sets the limits for closed-loop duty cycles.
        '''
        self.maxDuty = 40
        self.minDuty = -40
        self.int_error = 0
        self.int_error_o = 0
        # self.ref = 0
        
    def update_inner(self,eul_ang,dt,ang_vel, ref):
        '''!
            @brief      Updates the duty cycle under closed-loop control.
            @details    This function is in charge of actually using the gains
                        to assign a duty cycle to a motor to minimize error.
            @param      omega_meas is the current velocity of the motor.
            @return     Duty percentage of one motor is returned.
            
        '''
        self.ang_vel = ang_vel
        self.eul_ang = eul_ang
        self.time_diff = dt
        self.ref = ref
        self.error = self.ref - self.eul_ang
        self.deriv_error = -self.ang_vel
        self.int_error += self.time_diff*self.error
        self.Duty = self.Kp_i* self.error + self.KI_i*self.int_error + self.deriv_error*self.Kd_i
        
        if self.Duty > self.maxDuty:
            self.Duty = self.maxDuty
        elif self.Duty < self.minDuty:
            self.Duty = self.minDuty
            
        return self.Duty
    
    def update_outer(self,eul_ang,dt,ang_vel, ref, contact):
        '''!
            @brief      Updates the duty cycle under closed-loop control.
            @details    This function is in charge of actually using the gains
                        to assign a duty cycle to a motor to minimize error.
            @param      omega_meas is the current velocity of the motor.
            @return     Duty percentage of one motor is returned.
            
        '''
        if contact == False:
            self.int_error_o = 0
            
        self.ang_vel_o = ang_vel
        self.eul_ang_o = eul_ang
        self.time_diff_o = dt
        self.ref_o = ref
        self.error_o = self.ref_o - self.eul_ang_o
        self.deriv_error_o = -self.ang_vel_o
        self.int_error_o += self.time_diff_o*self.error_o
        self.Duty_o = self.Kp_o* self.error_o + self.KI_o*self.int_error_o + self.deriv_error_o*self.Kd_o
        
        if self.Duty_o > 10:
            self.Duty_o = 10
        elif self.Duty_o < -10:
            self.Duty_o = -10
            
        return self.Duty_o
        
    def set_gain_inner(self,Kp,KI,Kd):
        '''!@brief      Sets the gain and velocity reference values.
            @details    This function passed the user-selected values for gain
                        and Vref and passes them to the update() function.
            @param      Kp is the share of the user-requested proportional gain.
            @param      Ki is the share of the user-requested integral gain. 
            @param      omega_ref is the velocity requested by the user in
                        taskUser.
        '''
        self.Kp_i = Kp
        self.KI_i = KI
        self.Kd_i = Kd

    def set_gain_outer(self,Kp,KI,Kd):
        '''!@brief      Sets the gain and velocity reference values.
            @details    This function passed the user-selected values for gain
                        and Vref and passes them to the update() function.
            @param      Kp is the share of the user-requested proportional gain.
            @param      Ki is the share of the user-requested integral gain. 
            @param      omega_ref is the velocity requested by the user in
                        taskUser.
        '''
        self.Kp_o = Kp
        self.KI_o = KI
        self.Kd_o = Kd

    