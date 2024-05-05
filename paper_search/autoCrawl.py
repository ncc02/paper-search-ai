# import schedule
# import time

# def daily_task():
#     # Đây là nơi bạn viết logic cho tác vụ mà bạn muốn thực thi mỗi ngày
#     print("Tác vụ hàng ngày đã được thực thi!")

# # Đặt tác vụ để chạy mỗi ngày lúc 8 giờ sáng
# schedule.every().day.at("08:00").do(daily_task)

# # Vòng lặp để tiếp tục kiểm tra và chạy các tác vụ được lập lịch
# while True:
#     schedule.run_pending()
#     time.sleep(60)  # Ngủ trong 1 phút trước khi kiểm tra lại lịch


import schedule
import time

def daily_task():
    # Đây là nơi bạn viết logic cho tác vụ mà bạn muốn thực thi mỗi 5 giây
    print("Tác vụ được thực thi mỗi 5 giây!")

# Đặt tác vụ để chạy mỗi 5 giây
schedule.every(5).seconds.do(daily_task)

# Vòng lặp để tiếp tục kiểm tra và chạy các tác vụ được lập lịch
while True:
    schedule.run_pending()
    time.sleep(1)  # Ngủ trong 1 giây trước khi kiểm tra lại lịch
