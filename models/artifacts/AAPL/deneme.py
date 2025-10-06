import pickle

# scaler_X.pkl dosyasının yolu
file_path = r"C:\Users\tunah\OneDrive\Masaüstü\FinanceML-Pipeline\models\artifacts\AAPL\target_scaler.pkl"

# Dosyayı aç
with open(file_path, "rb") as f:
    scaler = pickle.load(f)

# Kullanılan sınıf tipini kontrol et
print(type(scaler))

# Eğer sklearn scaler ise, özellikler hakkında bilgiler
try:
    print("Scale (std):", getattr(scaler, 'scale_', None))
    print("Mean:", getattr(scaler, 'mean_', None))
    print("Min:", getattr(scaler, 'data_min_', None))
    print("Max:", getattr(scaler, 'data_max_', None))
    print("Feature range:", getattr(scaler, 'feature_range', None))
except Exception as e:
    print("Özellikler okunamadı:", e)
