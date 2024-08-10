import arrow
import http.client
import json
import ssl
import certifi
from tkinter import messagebox
import customtkinter
import cv2


def getsysdate():
    return arrow.now().format('YYYY-MM-DD HH:mm')


def class_attendance():
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("green")

    root = customtkinter.CTk()
    root.title("Scan Attendance")
    root.geometry("400x200")
    root.withdraw()  # hides the main window

    def scan_qr_code(frame):
        qr_code_detector = cv2.QRCodeDetector()
        text, points, _ = qr_code_detector.detectAndDecode(frame)
        if text:
            print("Data: ", text)
            return text
        else:
            return None

    cap = cv2.VideoCapture(0)

    student_number = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        qr_data = scan_qr_code(frame)
        if qr_data:
            print("QR Code Data: ", qr_data)
            student_number = qr_data
            break

        cv2.imshow("QR Code Scanner", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not student_number:
        messagebox.showinfo("Information", "No student number provided. Exiting...")
        return

    class_date = getsysdate()

    conn = http.client.HTTPSConnection("apex.oracle.com", context=ssl.create_default_context(cafile=certifi.where()))
    api_url = "/pls/apex/ifs_4255739/tutorials/tutorial_classes"
    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"adr": class_date, "std": student_number})

    try:
        conn.request("POST", api_url, body=payload, headers=headers)
        response = conn.getresponse()

        if response.status == 200:
            messagebox.showinfo("Success", "Attendance updated successfully.")
        else:
            messagebox.showerror("Error", f"Failed to update attendance. Status code: {response.status}")
            response_data = response.read().decode('utf-8')
            print(f"Response: {response_data}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to update attendance. Error: {e}")
    finally:
        conn.close()

    root.mainloop()


if __name__ == "__main__":
    class_attendance()
