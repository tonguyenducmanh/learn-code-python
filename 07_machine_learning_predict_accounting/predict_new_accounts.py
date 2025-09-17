import joblib
import pandas as pd

def predict_with_conditions(input_data):
    # Load the saved model and encoders
    model = joblib.load('account_prediction_model.joblib')
    label_encoders = joblib.load('label_encoders.joblib')
    target_encoder = joblib.load('target_encoder.joblib')
    
    # Convert input data to match training format
    encoded_input = {}
    for column, value in input_data.items():
        if column in label_encoders:
            try:
                encoded_input[column] = label_encoders[column].transform([str(value)])[0]
            except ValueError as e:
                print(f"Warning: Value '{value}' not seen during training for feature '{column}'")
                # Use the most frequent value as fallback
                encoded_input[column] = label_encoders[column].transform([label_encoders[column].classes_[0]])[0]
    
    # Create input array
    X_pred = pd.DataFrame([encoded_input])
    
    # Make prediction
    pred = model.predict(X_pred)
    account_pair = target_encoder.inverse_transform(pred)[0]
    debit_account, credit_account = account_pair.split('_')
    
    return debit_account, credit_account

if __name__ == '__main__':
    # Example 1: Regular sale of goods
    test_input1 = {
        'Hình thức bán hàng': 'Bán hàng hóa trong nước',
        'Phương thức thanh toán': 'Chưa thanh toán',
        'Kiêm phiếu xuất kho': 'Không',
        'Lập kèm hóa đơn': 'Nhận kèm hóa đơn',
        'Đã lập hóa đơn': 'Có',
        'Mã hàng': 'BANHMY',
        'Tên hàng': 'Bánh mỳ (HH thông thường)',
        'Là dòng ghi chú': 'Không',
        'Hàng khuyến mại': 'Không',
        'ĐVT': 'Cái'
    }
    
    # Example 2: Service sale
    test_input2 = {
        'Hình thức bán hàng': 'Bán dịch vụ',
        'Phương thức thanh toán': 'Chưa thanh toán',
        'Kiêm phiếu xuất kho': 'Không',
        'Lập kèm hóa đơn': 'Nhận kèm hóa đơn',
        'Đã lập hóa đơn': 'Có',
        'Mã hàng': 'CPMH',
        'Tên hàng': 'Chi phí mua hàng',
        'Là dòng ghi chú': 'Không',
        'Hàng khuyến mại': 'Không',
        'ĐVT': ''
    }
    
    # Make predictions
    print("\nTest Case 1 - Regular sale:")
    debit1, credit1 = predict_with_conditions(test_input1)
    print(f"Debit account (TK Nợ): {debit1}")
    print(f"Credit account (TK Có): {credit1}")
    
    print("\nTest Case 2 - Service sale:")
    debit2, credit2 = predict_with_conditions(test_input2)
    print(f"Debit account (TK Nợ): {debit2}")
    print(f"Credit account (TK Có): {credit2}")
