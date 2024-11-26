# TC01 - MySQL Housing

## Yêu cầu

* Docker v27.1.1
* Docker Compose v2.29.1
    * MySQL Server 8.0


## Mô tả dữ liệu

Tập dữ liệu dự đoán giá nhà - Bài toán hồi quy (regression). Các cột và mô tả của dữ liệu bao gồm :
* price : Giá nhà
* area : Diện tích
* bedrooms: Số phòng ngủ
* bathrooms: Số phòng tắm
* stories: Số tầng
* mainroad: Có nằm trên trục đường chính hay không
* guestroom: Có phòng cho khách hay không
* basement: Có tầng hầm hay không 
* hotwaterheating: Có bình nóng lạnh hay không 
* airconditioning: Có điều hoà hay không

## Kết quả kiểm thử

Hệ thống tự động lựa chọn đúng kiểu dữ liệu của cột và đưa ra giải pháp biến đổi dữ liệu tương ứng.

* price : Numeric
* area : Numeric
* bedrooms: Numeric
* bathrooms: Numeric
* stories: Numeric
* mainroad: Boolean
* guestroom: Boolean
* basement: Boolean
* hotwaterheating: Boolean
* airconditioning: Boolean
* 

