// ====== BOOKING SYSTEM FUNCTIONS ======

// Service Selection
function toggleService(serviceId) {
    const checkbox = document.getElementById('service' + serviceId);
    const card = checkbox.closest('.service-card');

    checkbox.checked = !checkbox.checked;

    if (checkbox.checked) {
        card.classList.add('selected');
    } else {
        card.classList.remove('selected');
    }

    updateServiceSummary();
}

function updateServiceSummary() {
    const selectedServices = document.querySelectorAll('input[name="services"]:checked');
    const totalPrice = Array.from(selectedServices).reduce((total, service) => {
        const card = service.closest('.service-card');
        const priceText = card.querySelector('.price').textContent;
        const price = parseInt(priceText.replace(/[^\d]/g, ''));
        return total + (price || 0);
    }, 0);

    // Update summary if exists
    const summaryElement = document.getElementById('service-summary');
    if (summaryElement) {
        summaryElement.textContent = formatCurrency(totalPrice);
    }
}

// Employee Selection
function selectEmployee(value) {
    document.querySelectorAll('input[name="employee"]').forEach(radio => {
        radio.checked = radio.value === value;
    });

    // Update UI
    document.querySelectorAll('.employee-card').forEach(card => {
        card.classList.remove('selected');
    });

    const selectedCard = document.querySelector(`input[value="${value}"]`)?.closest('.employee-card');
    if (selectedCard) {
        selectedCard.classList.add('selected');
    }
}

// Time Selection
function selectTimeSlot(time) {
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.classList.remove('selected');
    });

    const selectedSlot = document.querySelector(`.time-slot[data-time="${time}"]`);
    if (selectedSlot) {
        selectedSlot.classList.add('selected');
        document.querySelector('select[name="appointment_time"]').value = time;
    }
}

// Date Selection
function selectDate(date) {
    document.querySelectorAll('.calendar-day').forEach(day => {
        day.classList.remove('selected');
    });

    const selectedDay = document.querySelector(`.calendar-day[data-date="${date}"]`);
    if (selectedDay) {
        selectedDay.classList.add('selected');
        document.querySelector('select[name="appointment_date"]').value = date;
    }
}

// Form Validation
function validateBookingForm(step) {
    let isValid = true;

    switch(step) {
        case 1:
            const name = document.querySelector('input[name="name"]');
            const phone = document.querySelector('input[name="phone_number"]');

            if (!name.value.trim()) {
                showNotification('Vui lòng nhập họ và tên', 'danger');
                isValid = false;
            }

            if (!validatePhoneNumber(phone.value)) {
                showNotification('Số điện thoại không hợp lệ', 'danger');
                isValid = false;
            }
            break;

        case 2:
            const selectedServices = document.querySelectorAll('input[name="services"]:checked');
            if (selectedServices.length === 0) {
                showNotification('Vui lòng chọn ít nhất một dịch vụ', 'danger');
                isValid = false;
            }
            break;
    }

    return isValid;
}

// Initialize booking system
document.addEventListener('DOMContentLoaded', function() {
    // Initialize selected states
    document.querySelectorAll('input[name="services"]:checked').forEach(checkbox => {
        checkbox.closest('.service-card')?.classList.add('selected');
    });

    const selectedEmployee = document.querySelector('input[name="employee"]:checked');
    if (selectedEmployee) {
        selectEmployee(selectedEmployee.value);
    }

    // Add click handlers for time slots
    document.querySelectorAll('.time-slot').forEach(slot => {
        slot.addEventListener('click', function() {
            if (!this.classList.contains('disabled')) {
                selectTimeSlot(this.dataset.time);
            }
        });
    });

    // Add click handlers for calendar days
    document.querySelectorAll('.calendar-day').forEach(day => {
        day.addEventListener('click', function() {
            if (!this.classList.contains('disabled')) {
                selectDate(this.dataset.date);
            }
        });
    });

    // Form submission validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const step = this.dataset.step;
            if (step && !validateBookingForm(parseInt(step))) {
                e.preventDefault();
            }
        });
    });
});

// ====== DYNAMIC SUMMARY CALCULATION ======
function calculateServiceSummary() {
    const selectedServices = document.querySelectorAll('input[name="services"]:checked');
    let totalPrice = 0;
    let totalDuration = 0;
    let servicesList = [];

    selectedServices.forEach(service => {
        const card = service.closest('.service-card');
        const price = parseFloat(card.querySelector('.price')?.dataset.price || 0);
        const duration = parseInt(card.querySelector('.duration')?.dataset.duration || 0);

        totalPrice += price;
        totalDuration += duration;
        servicesList.push({
            name: card.querySelector('h6').textContent,
            price: price,
            duration: duration
        });
    });

    return { totalPrice, totalDuration, servicesList };
}

function updateSummaryDisplay() {
    const summary = calculateServiceSummary();

    // Update summary box if exists
    const summaryBox = document.querySelector('.summary-box');
    if (summaryBox) {
        // Update total price
        const totalPriceElement = summaryBox.querySelector('.total-price');
        if (totalPriceElement) {
            totalPriceElement.textContent = formatCurrency(summary.totalPrice);
        }

        // Update total duration
        const totalDurationElement = summaryBox.querySelector('.total-duration');
        if (totalDurationElement) {
            totalDurationElement.textContent = `${summary.totalDuration} phút`;
        }

        // Update services list
        const servicesListElement = summaryBox.querySelector('.services-list');
        if (servicesListElement) {
            servicesListElement.innerHTML = summary.servicesList.map(service => `
                <div class="d-flex justify-content-between border-bottom pb-1 mb-1">
                    <span>${service.name}</span>
                    <span>${formatCurrency(service.price)}đ</span>
                </div>
            `).join('');
        }
    }

    // Store in session for server-side use
    if (summary.totalPrice > 0) {
        sessionStorage.setItem('booking_summary', JSON.stringify(summary));
    }
}

// Listen for service selection changes
document.addEventListener('change', function(e) {
    if (e.target.matches('input[name="services"]')) {
        updateSummaryDisplay();
    }
});
// ====== ENHANCED FORM VALIDATION ======
function validateStep1() {
    const name = document.querySelector('input[name="name"]');
    const phone = document.querySelector('input[name="phone_number"]');
    const email = document.querySelector('input[name="email"]');
    const errors = [];

    // Name validation
    if (!name.value.trim()) {
        errors.push({ field: name, message: 'Vui lòng nhập họ và tên' });
        name.classList.add('is-invalid');
    } else if (name.value.length < 2) {
        errors.push({ field: name, message: 'Tên phải có ít nhất 2 ký tự' });
        name.classList.add('is-invalid');
    } else {
        name.classList.remove('is-invalid');
    }

    // Phone validation (Vietnamese phone number)
    const phoneRegex = /(0[3|5|7|8|9])+([0-9]{8})\b/;
    if (!phone.value.trim()) {
        errors.push({ field: phone, message: 'Vui lòng nhập số điện thoại' });
        phone.classList.add('is-invalid');
    } else if (!phoneRegex.test(phone.value.replace(/\s/g, ''))) {
        errors.push({ field: phone, message: 'Số điện thoại không hợp lệ' });
        phone.classList.add('is-invalid');
    } else {
        phone.classList.remove('is-invalid');
    }

    // Email validation (optional)
    if (email.value && !validateEmail(email.value)) {
        errors.push({ field: email, message: 'Email không hợp lệ' });
        email.classList.add('is-invalid');
    } else {
        email.classList.remove('is-invalid');
    }

    return errors;
}

function validateStep2() {
    const selectedServices = document.querySelectorAll('input[name="services"]:checked');
    const errors = [];

    if (selectedServices.length === 0) {
        errors.push({ field: null, message: 'Vui lòng chọn ít nhất một dịch vụ' });
        showNotification('Vui lòng chọn ít nhất một dịch vụ', 'danger');
    }

    return errors;
}

