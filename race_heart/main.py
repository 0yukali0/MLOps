from ultralytics import YOLO

def main():
    # 載入預訓練模型 (可選 yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt)
    model = YOLO("yolov8n.pt")

    # 開始訓練
    results = model.train(
        data="dataset.yaml",   # YAML 檔路徑
        epochs=10,            # 訓練輪數
        imgsz=512,             # 圖片大小
        batch=16,              # 批次大小
        workers=4,             # dataloader 線程數
        name="custom_yolo_train", # 儲存目錄名稱
        device=0               # GPU id，若無GPU可改為 "cpu"
    )

    # 訓練結果自動存到 runs/detect/custom_yolo_train/
    print("✅ 訓練完成！模型已儲存至：", results.save_dir)

    # 驗證模型
    metrics = model.val()
    print("📊 驗證結果：", metrics)

    # 用模型做預測
    #preds = model.predict(source="./data/training_image/patient0001", save=True)
    #print("📸 預測結果輸出於：runs/detect/predict/")

if __name__ == "__main__":
    main()
