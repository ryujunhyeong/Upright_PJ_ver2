
class UserFig:
    bodyLength_R: int
    bodyLength_L: int

    def Set_User(self, bodyLength_R: int, bodyLength_L: int):
        self.bodyLength_R = bodyLength_R
        self.bodyLength_L = bodyLength_L
        
userFig = UserFig()     # 보정값을 위한 유저 객체, 정자세값을 담음
userLearn = UserFig()   # 학습값을 위한 유저 객체, 오류값 측정 기준값을 담음