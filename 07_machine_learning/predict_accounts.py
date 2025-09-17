import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load and preprocess data
def load_data():
    # Read CSV with different encoding, skip first 2 rows
    df = pd.read_csv('Ban_hang_va_ban_dich_vu.csv', encoding='utf-8-sig', skiprows=2)
    
    # Print column names for debugging
    print("Available columns:")
    for col in df.columns:
        print(col)
    
    # Extract target columns (account pairs)
    df['account_pair'] = df['TK Tiền/Chi phí/Nợ'].astype(str) + '_' + df['TK Doanh thu/Có'].astype(str)
    
    # Select features for prediction
    features = ['Hình thức bán hàng', 'Phương thức thanh toán', 'Kiêm phiếu xuất kho',
               'Lập kèm hóa đơn', 'Đã lập hóa đơn', 'Mã hàng', 'Tên hàng', 'Là dòng ghi chú',
               'Hàng khuyến mại', 'ĐVT']
    
    # Create label encoders for categorical features
    label_encoders = {}
    X = df[features].copy()
    for column in features:
        label_encoders[column] = LabelEncoder()
        X[column] = label_encoders[column].fit_transform(df[column].astype(str))
    
    # Encode target variable
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(df['account_pair'])
    
    return X, y, label_encoders, target_encoder

# Train model
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    train_score = clf.score(X_train, y_train)
    test_score = clf.score(X_test, y_test)
    
    print(f"Training accuracy: {train_score:.4f}")
    print(f"Testing accuracy: {test_score:.4f}")
    
    return clf

# Save model and encoders
def save_model(model, label_encoders, target_encoder):
    joblib.dump(model, 'account_prediction_model.joblib')
    joblib.dump(label_encoders, 'label_encoders.joblib')
    joblib.dump(target_encoder, 'target_encoder.joblib')

# Predict account pairs
def predict_accounts(model, label_encoders, target_encoder, input_data):
    # Convert input data to match training format
    encoded_input = {}
    for column, value in input_data.items():
        if column in label_encoders:
            encoded_input[column] = label_encoders[column].transform([str(value)])[0]
    
    # Create input array
    X_pred = pd.DataFrame([encoded_input])
    
    # Make prediction
    pred = model.predict(X_pred)
    account_pair = target_encoder.inverse_transform(pred)[0]
    
    return account_pair.split('_')

if __name__ == '__main__':
    # Load and preprocess data
    X, y, label_encoders, target_encoder = load_data()
    
    # Train model
    model = train_model(X, y)
    
    # Save model and encoders
    save_model(model, label_encoders, target_encoder)
    
    # Example prediction
    test_input = {
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
    
    # Get prediction
    debit_account, credit_account = predict_accounts(model, label_encoders, target_encoder, test_input)
    print(f"\nPredicted accounts for test input:")
    print(f"Debit account (TK Nợ): {debit_account}")
    print(f"Credit account (TK Có): {credit_account}")
