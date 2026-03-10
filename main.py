from data import fetch_ohlcv

# Gọi hàm từ file data.py
df = fetch_ohlcv()

# In 5 dòng cuối cùng của bảng dữ liệu
print(df.tail())