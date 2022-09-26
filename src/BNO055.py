'''!
    @file       BNO055.py
    
    @brief      Driver to be used with the BNO055 IMU connected to the Nucelo 
                board.
    
    @details    This driver interacts directly with the BNO055. It initializes
                the IMU and puts it in operatiing mode. Additionally, it reads
                and writes the calibration coefficients to the IMU. The main 
                purpose of the driver is to read the data from the IMU. The 
                Euler Angles and angular velocites are read from here. 
    
                The source code can be found at my repository under "Final Lab":
                https://bitbucket.org/jakelesher/me-305-labs
                
    @author     Jake Lesher
    @author     Daniel Xu
    @date       2/24/2022
    
'''
import pyb, utime
from pyb import I2C

class BNO055:
    '''!@brief      A BNO055 IMU driver class.
        @details    Objects of this class can be used to configure the BNO055 IMU.
                    IMU objects created from this class are able be read data from
                    the IMU using I2C. This includes calibration data, euler angles,
                    and angular velocity. 
                    
    '''
    def __init__(self, i2c):
        '''!@brief   Initializes the BNO055 IMU   
            @param   i2c The I2C controller object that is associated with the
                     IMU
    
            
        '''
        self.i2c = i2c
        self.addr = self.i2c.scan()[0]
        
        self.cal_coef = [0]*22
        self.calbuff = bytearray(22)
        
        self.OPR_MODE = 0x3D # The register for operating mode.
        self.config_mode = 0b00000000 # The byte to send to OPR_MODE for configuation.
        self.NDoF_mode = 0b00001100 # The byte to send to OPR_MODE for NDoF.
        self.i2c.mem_write(self.config_mode, self.addr, self.OPR_MODE)
        utime.sleep_ms(20)
        

        
    def mode(self, modenum):
        '''!@brief  Sets the mode for IMU at which it will be operating in.      
            @param  modenum will be set to 0 for config mode and 1 for NDoF mode.     
            
        '''
        if modenum == 0:
            self.i2c.mem_write(self.config_mode, self.addr, self.OPR_MODE)
        elif modenum == 1:
            self.i2c.mem_write(self.NDoF_mode, self.addr, self.OPR_MODE)

        
    def status(self):
        '''!@brief   Identifies the calibration status of the IMU 
            @details This function reads the calibration states from the IMU. 
                     It returns a 3 if the sensor is calibrated. 
            @return  self.mag_stat Calibration status of magnetometer
            @return  self.acc_stat Calibration status of the accelerometer
            @return  self.gyr_stat Calibration status of the gyroscope
            @return  self.sys_stat Calibration statuse of the system
            
        '''
        self.cal_byte = self.i2c.mem_read(1, self.addr, 0x35)[0]
        self.mag_stat = self.cal_byte & 0b00000011
        self.acc_stat = (self.cal_byte & 0b00001100)>>2
        self.gyr_stat = (self.cal_byte & 0b00110000)>>4
        self.sys_stat = (self.cal_byte & 0b11000000)>>6
        return self.mag_stat, self.acc_stat, self.gyr_stat, self.sys_stat

    def read_coef(self):
        '''!@brief  Reads the calibration coefficients when the system is fully 
                    calibrated.        
            @return self.cal_coef The calibration coefficients of the IMU.     
            
        '''
        self.reg_addr = 0x55
        self.cal_coef = self.i2c.mem_read(self.calbuff, self.addr, self.reg_addr)
        return self.cal_coef
        
        
    def write_coef(self, cal_coefs):
        '''!@brief  Writes existing calibration coefficients into the IMU         
            @param  cal_coefs The calibration coefficients from previous 
                    calibrations         
            
        '''
        self.reg_addr = 0x55
        self.i2c.mem_write(cal_coefs, self.addr, self.reg_addr)

    
    def read_angle(self):
        '''!@brief  Reads the euler angle data from IMU and merges MSB and LSB       
            @return (self.Roll, self.Pitch, self.Heading) Tuple of Euler Angles   
            
        '''
        Euler = self.i2c.mem_read(6, self.addr, 0x1A)
        
        self.Heading = (Euler[1] << 8 | Euler[0])
        if self.Heading > 32767:
            self.Heading -= 65536
        
        self.Roll = (Euler[3] << 8 | Euler [2])
        if self.Roll > 32767:
            self.Roll -= 65536
        
        self.Pitch  = (Euler[5] << 8 | Euler[4])       
        if self.Pitch > 32767:
            self.Pitch -= 65536
        
        return (self.Roll, self.Pitch, self.Heading)
        
        
    def read_omega(self):
        '''!@brief  Reads the angular velocity data from IMU and merges MSB 
                    and LSB           
            @return (self.w_x,self.w_y,self.w_z) Tuple of angular velocity     
            
        '''
        w = self.i2c.mem_read(6, self.addr, 0x14)
        
        self.w_y = (w[1] << 8 | w[0])
        if self.w_y > 32767:
            self.w_y -= 65536
        self.w_y *= -1
        
        self.w_x = (w[3] << 8 | w[2])
        if self.w_x > 32767:
            self.w_x -= 65536
        
        self.w_z = (w[5] << 8 | w[4])
        if self.w_z > 32767:
            self.w_z -= 65536
        
        return (self.w_x,self.w_y,self.w_z)

if __name__ == '__main__':
    # Adjust the following code to write a test program.
    
    i2c = I2C(1, I2C.CONTROLLER)
    IMU = BNO055(i2c)
    IMU.mode(1)
    print(f'{IMU.read_coef()}')
    
    # while True:
    #     if IMU.status() == (3,3,3,0):
    #         print(f'The angles are {IMU.read_angle()}.')
    #         #print(f'The omegas are {IMU.read_omega()}.')
    #         utime.sleep(1)
            
    #     else:
    #         print(f'{IMU.status()}')
            
    
