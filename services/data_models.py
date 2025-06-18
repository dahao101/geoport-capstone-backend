from pydantic import BaseModel
from typing import Optional,Dict, List
from fastapi import Depends,HTTPException,Header

class CreateAccountData(BaseModel):
    idToken: str
    name: str
    role: str
    userType: str
    age: int
    sex: str
    longitude: float
    latitude: float
    contactNumber: str


class UpdatePassword(BaseModel):
    user_id:str  
    new_password: str



class CreateReport(BaseModel):
    DateAndTime: str
    Severity: str
    TypeOfReport: str
    image: str
    location: Dict[str, str]
    passable: str
    reference: str
    reporter: str
    status:str

class Subscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]

class RegisterPushNotification(BaseModel):
    endpoint: str
    keys: Dict[str, str]


class UpdateEmailVerifypin(BaseModel):
    inputted_pin: str

class UpdateEmail(BaseModel):
    user_id: str
    new_email:str


class UpdateName(BaseModel):
    user_id: str
    new_name: str
    image_link: str = None

class SaveLogs(BaseModel):
   event: str
   date: str
   browser: str

class PasswordSendPin(BaseModel):
    user_id: str

class VerifyPin(BaseModel):
    inputted_pin:int
    user_id:str


class UpdateUserRequest(BaseModel):
    imageUrl: str


class CreateUserAccount(BaseModel):
      name:str
      age:int
      sex: str
      contactNumber: str
      role: str
      status: str
      uid: str


class UpdateNameData(BaseModel):
    user_id: str
    new_name: str

class ChangeNumberData(BaseModel):
    inputted_pin: str

class UserInfoUpdate(BaseModel):
    new_name: str
    new_profile: str

class app_change_password_send(BaseModel):
    email:str

class app_change_password_verify(BaseModel):
    pin:str
    email:str
class change_password_data(BaseModel):
    new_password:str
    email:str

class app_change_email_verify(BaseModel):
    inputted_pin:str

# class ApplicationModel(BaseModel):
#     def change_password():

class change_new_email(BaseModel):
    new_email:str


class NumberData(BaseModel):
    new_number: str

class ApplyTokenData(BaseModel):
    expoPushToken:str


class UpdateNameData(BaseModel):
    user_id:str
    new_name:str

class forgotPasswordSendPin(BaseModel):
    email:str

class forgotPasswordVerifyPin(BaseModel):
    pin:str
    email:str

class RemoveReport(BaseModel):
    report_id:str
    currentVersion:int



class CreateResponder(BaseModel):
    name: str
    email:str
    password:str
    number:str

class UpdateResponder(BaseModel):
    id:str
    name: str
    updateEmail:str
    phone:str

class DisableResponder(BaseModel):
    user_id:str
    status:str

class RemoveResponder(BaseModel):
    user_id:str


class reverseLocationData(BaseModel):
    latitude: float
    longitude: float

class RouteFunctionData(BaseModel):
    start_latitude: float
    start_longitude: float
    end_latitude: float
    end_longitude: float

class DefectCoordinates(BaseModel):
    latitude: float
    longitude: float

class RerouteFunctionData(BaseModel):
    start_latitude: float
    start_longitude: float
    end_latitude: float
    end_longitude: float
    defect_nodes: List[DefectCoordinates]


class GenerateRoomId(BaseModel):
    room_id:str

class GetRoomId(BaseModel):
    user_id:str

class LivekitTokenGenerator(BaseModel):
    user_id:str
    type:str

class SendCallSignal(BaseModel):
    user_id:str
    type: str
    room_token:str