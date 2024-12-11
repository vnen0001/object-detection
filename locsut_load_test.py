from locust import HttpUser,task,events,between
import os 
import time
from locust.event import EventHook
#from locust.exception import StopUser
import sys

class Image_report(HttpUser):
    wait_time = between(1,3)
    host =  f'<url>'
    spawn_rate = 10
    image_dir = '/home/ubuntu/object_detection/object_detection/inputfolder'
    total_request = 0 
    concurrent_user = 1
    start_time = 0
    failed= 0
    request_success = EventHook()
    failed_request = EventHook()
    quitting = EventHook()
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def on_start(self):
        pass
        
    @task
    def send_req(self):
      
        for image in os.listdir(self.image_dir):
            path = os.path.join(self.image_dir,image)
            self.total_request +=1
            self.start_time = time.time()
            response = self.client.post('/',files = {'file': open(path,'rb')})
            print(response.status_code)
            if response.status_code != 200:
                self.failed +=1
                if self.concurrent_user >1:
                    self.concurrent_user -=1
                    self.failed_request.fire(user=self.environment.runner.user_count)

                    #self.on_stop()
                else:
                    #self.on_stop()
                    print('--')
            else :
                print(response.text)
                print('The count of fail before increasing',self.failed)
                self.concurrent_user  = self.environment.runner.user_count + 1 
                self.request_success.fire(users = self.environment.runner.user_count,response_time = self.environment.runner.stats.total.response_times)
                time_duration = time.time() - self.start_time
                print(time_duration)
                print('Failed _req',self.failed)
                if self.failed==0 and self.environment.runner.user_count < 20:
                    avergae_respone_time = sum(self.environment.runner.stats.total.response_times)/len(self.environment.runner.stats.total.response_times)
                    print("Average respone in (ms)",avergae_respone_time)
                    if avergae_respone_time < 400 :
                        self.environment.runner.start(self.environment.runner.user_count +1,spawn_rate=10)
                        print("User incrased ",self.environment.runner.user_count)
                else:
                    print('The Max User is ', self.environment.runner.user_count)
                    print('Recieved a failed request')
                    self.quitting.fire(environment = self.environment)
                    self.environment.runner.quit()

                        

       
@Image_report.request_success.add_listener
def success_req(users,response_time,**kwargs):
    print('The current user ', users)
    print(sum(response_time)/len(response_time))

@Image_report.failed_request.add_listener
def failed_users(user,**kwargs):
    print('The user failed',user)
