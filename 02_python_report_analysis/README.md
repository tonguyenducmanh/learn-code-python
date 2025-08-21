tôi có 1 yêu cầu như sau:
#### Phân tích báo cáo tài chính, nhân sự. ##### Bài toán: Từ các dữ liệu trên phần mềm AMIS MXH (Doanh thu, Nhân sự). Hãy đưa ra bài phân tích về tình hình tăng trưởng của Công ty. ##### Input: Dữ liệu cần lên báo cáo: Doanh thu, Nhân sự từ 2 bảng trên AMIS MXH.
Dữ liệu mẫu về nhân sự:
[
    {
        "EmployeePercent": null,
        "ID": "1",
        "OrganizationUnitCode": null,
        "Quantity": 3212,
        "LastQuantity": 2906,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "2",
        "OrganizationUnitCode": null,
        "Quantity": 3261,
        "LastQuantity": 2889,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "3",
        "OrganizationUnitCode": null,
        "Quantity": 3269,
        "LastQuantity": 2868,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "4",
        "OrganizationUnitCode": null,
        "Quantity": 3249,
        "LastQuantity": 2837,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "5",
        "OrganizationUnitCode": null,
        "Quantity": 3347,
        "LastQuantity": 2870,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "6",
        "OrganizationUnitCode": null,
        "Quantity": 3497,
        "LastQuantity": 2930,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "7",
        "OrganizationUnitCode": null,
        "Quantity": 3670,
        "LastQuantity": 3010,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "8",
        "OrganizationUnitCode": null,
        "Quantity": 3710,
        "LastQuantity": 3042,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "9",
        "OrganizationUnitCode": null,
        "Quantity": 0,
        "LastQuantity": 3090,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "10",
        "OrganizationUnitCode": null,
        "Quantity": 0,
        "LastQuantity": 3125,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "11",
        "OrganizationUnitCode": null,
        "Quantity": 0,
        "LastQuantity": 3172,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    },
    {
        "EmployeePercent": null,
        "ID": "12",
        "OrganizationUnitCode": null,
        "Quantity": 0,
        "LastQuantity": 3208,
        "ReceiveQuantity": null,
        "TerminateQuantity": null
    }
]
Dữ liệu mẫu về doanh số:
[
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 120.11,
        "xAxis": "1",
        "TotalRevenue": 1692.67
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 192.24,
        "xAxis": "2",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 236.45,
        "xAxis": "3",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 267.99,
        "xAxis": "4",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 282.51,
        "xAxis": "5",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 267.52,
        "xAxis": "6",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 218.62,
        "xAxis": "7",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 107.23,
        "xAxis": "8",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 0,
        "xAxis": "9",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 0,
        "xAxis": "10",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 0,
        "xAxis": "11",
        "TotalRevenue": 0
    },
    {
        "Name": null,
        "RevenueAmount": 0,
        "RevenuePercent": 0,
        "TotalAmount": 0,
        "xAxis": "12",
        "TotalRevenue": 0
    }
]

tạo giúp tôi 1 luồng code python sử dụng langraph, có 4 node chính:
Node 1 sẽ đọc nguồn vào là 2 file json chứa giá trị biểu đồ nhân sự và biểu đồ doanh số của năm 2025, và phân tích kết quả, nội dung của báo cáo có thể tự do sáng tạo nhưng phải chuyên nghiệp và phân tích được các điểm chính trong số liệu
Node 2 sẽ dựa vào kết quả của node 1 và tóm tắt ra 3 tiêu chí: điểm tích cực, điểm hạn chế, lời khuyên cho doanh nghiệp
Node 3 sẽ thực hiện xuất kết quả phân tích ở node 1 ra HTML
Node 4 sẽ dựa vào kết quả của node 3 và chuyển HTML thành file PDF có thể xem được
Tiêu đề file kết quả phân tích phải bắt đầu bằng Công ty Cổ Phần MISA báo cáo về tình hình nhân sự và doanh số năm 2025


### yêu cầu về công nghệ

sử dụng openapi, langraph để xử lý
hãy tạo prompt chi tiết cho mỗi node
sau đó khi chạy đến node nào thì sẽ nhờ openai phân tích rồi hoàn thành mới chuyển sang node tiếp theo