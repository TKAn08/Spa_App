from datetime import datetime, timedelta


def format_date_vietnamese(data):
    weekdays_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    data = data
    results = []
    for d in data:
        results.append((weekdays_vi[d[0].weekday()], d[1]))
    return results

def format_currency(value):
    """
    Format số tiền thành định dạng VND
    Ví dụ: 1500000 -> 1.500.000đ
    """
    if value is None:
        return "0đ"

    try:
        # Chuyển thành số
        num = float(value)

        # Format với dấu phân cách hàng nghìn
        formatted = "{:,.0f}".format(num).replace(",", ".")

        return f"{formatted}đ"
    except (ValueError, TypeError):
        # Nếu không phải số, trả về nguyên bản
        return f"{value}đ"


def format_date(value, format_string='%d/%m/%Y'):
    """
    Format datetime/date thành string
    Ví dụ: datetime(2024, 12, 25) -> 25/12/2024
    """
    if value is None:
        return ""

    # Nếu là string, try parse thành datetime
    if isinstance(value, str):
        try:
            # Thử parse các định dạng phổ biến
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']:
                try:
                    value = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue
        except:
            return value

    # Nếu có method strftime (datetime/date object)
    if hasattr(value, 'strftime'):
        try:
            return value.strftime(format_string)
        except:
            return str(value)

    return str(value)


def format_datetime(value):
    """Format datetime thành dd/mm/yyyy HH:MM"""
    return format_date(value, '%d/%m/%Y %H:%M')


def format_time(value):
    """Format time thành HH:MM"""
    if value is None:
        return ""

    if hasattr(value, 'strftime'):
        return value.strftime('%H:%M')

    if isinstance(value, str):
        # Nếu là string, lấy phần time
        try:
            dt = datetime.strptime(value, '%H:%M:%S')
            return dt.strftime('%H:%M')
        except:
            try:
                dt = datetime.strptime(value, '%H:%M')
                return dt.strftime('%H:%M')
            except:
                return value

    return str(value)


def format_duration(minutes):
    """Format số phút thành giờ:phút"""
    if minutes is None:
        return "0 phút"

    try:
        mins = int(minutes)
        if mins < 60:
            return f"{mins} phút"
        else:
            hours = mins // 60
            remaining_mins = mins % 60
            if remaining_mins == 0:
                return f"{hours} giờ"
            else:
                return f"{hours} giờ {remaining_mins} phút"
    except (ValueError, TypeError):
        return f"{minutes} phút"


def format_phone(phone_number):
    """Format số điện thoại"""
    if not phone_number:
        return ""

    phone = str(phone_number).strip()

    # Xóa tất cả khoảng trắng và ký tự đặc biệt
    phone = ''.join(filter(str.isdigit, phone))

    if len(phone) == 10:
        return f"{phone[:4]} {phone[4:7]} {phone[7:]}"
    elif len(phone) == 11:
        return f"{phone[:4]} {phone[4:7]} {phone[7:]}"
    else:
        return phone_number