from django.db import models
from datetime import datetime


class employee(models.Model):
    full_name = models.CharField(max_length=250, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    auth_level = models.FloatField(blank=True, null=True)
    password = models.CharField(max_length=50, blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True, null=True)
    active = models.IntegerField(default=1, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    department = models.CharField(max_length=250, blank=True, null=True)
    position = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return str(self.pk) + " " + str(self.full_name)


class admin_conversation(models.Model):
    employee = models.ForeignKey(employee,
                                 on_delete=models.CASCADE, blank=True, null=True)
    conversations = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return str(self.employee) + " " + str(self.conversations)


class attendance(models.Model):
    check_in = models.DateTimeField(blank=True, null=True)
    check_out = models.DateTimeField(blank=True, null=True)
    employee = models.ForeignKey(employee, on_delete=models.CASCADE, blank=True,
                                 null=True, related_name='employee_attendance')

    def __str__(self):
        return str(self.employee)


class inventory(models.Model):
    item_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.IntegerField(default=0, blank=True, null=True)
    item_type = models.CharField(default='unknown', max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.item_name)


class inventory_log(models.Model):
    item = models.ForeignKey(inventory, on_delete=models.CASCADE, blank=True, null=True)
    log_date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    action_by = models.ForeignKey(employee, on_delete=models.CASCADE, blank=True, null=True)
    log = models.TextField(blank=True, null=True)
    type = models.CharField(default='unknown', max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.item)


class stock(models.Model):
    item = models.ForeignKey(inventory, on_delete=models.CASCADE, blank=True, null=True)
    current = models.IntegerField(blank=True, null=True)
    type = models.IntegerField(default=0, blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    action_by = models.ForeignKey(employee, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.item) + " " + str(self.current)


class expense(models.Model):
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    item = models.CharField(max_length=250, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    message = models.TextField(default='n/a', blank=True, null=True)
    action_by = models.ForeignKey(employee, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.item + " " + str(self.amount)


class revenue(models.Model):
    source = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    message = models.TextField(default='n/a', blank=True, null=True)
    action_by = models.ForeignKey(employee, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.source)


class salary(models.Model):
    employee = models.ForeignKey('staff.employee', on_delete=models.CASCADE, blank=True,
                                 null=True, related_name="hotel_employee")
    pay_date = models.DateTimeField(blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True, null=True)
    amount = models.FloatField(blank=True, null=True)
    action_by = models.ForeignKey('staff.employee', on_delete=models.CASCADE, blank=True,
                                  null=True, related_name="admin_employee")

    def __str__(self):
        return str(self.employee)


class department(models.Model):
    department_title = models.CharField(max_length=100, blank=True, null=True)
    department_val = models.FloatField(blank=True, null=True)
    auth_level = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.department_title


class authentication_level(models.Model):
    level_title = models.CharField(max_length=100, blank=True, null=True)
    level_val = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.level_title


class position(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    no_of_staff = models.IntegerField(blank=True, null=True)
    department = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

