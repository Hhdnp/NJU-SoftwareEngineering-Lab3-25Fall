import tkinter as tk
from tkinter import ttk
from datetime import datetime
from tkinter import messagebox
from models import transactions, budgets, data_manager


class BudgetWindow:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        # 标题
        tk.Label(self.frame, text="预算管理", font=("Arial", 16)).pack(pady=10)

        # 预算设置框架
        budget_frame = tk.LabelFrame(self.frame, text="预算设置")
        budget_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(budget_frame, text="月度预算:").grid(
            row=0, column=0, sticky="w", pady=5)
        self.budget_entry = tk.Entry(budget_frame)
        self.budget_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        self.budget_entry.insert(0, str(budgets[0].amount))

        tk.Button(budget_frame, text="更新预算", command=self.update_budget,
                  bg="#4CAF50", fg="white").grid(row=0, column=2, padx=5)

        budget_frame.columnconfigure(1, weight=1)

        # 月度概览框架
        overview_frame = tk.LabelFrame(self.frame, text="月度概览")
        overview_frame.pack(fill="x", padx=20, pady=10)

        self.budget_label = tk.Label(overview_frame, text="预算: 0")
        self.budget_label.pack(side="left", padx=10)

        self.expense_label = tk.Label(overview_frame, text="支出: 0")
        self.expense_label.pack(side="left", padx=10)

        self.income_label = tk.Label(overview_frame, text="收入: 0")
        self.income_label.pack(side="left", padx=10)

        self.balance_label = tk.Label(overview_frame, text="余额: 0")
        self.balance_label.pack(side="left", padx=10)

        # 搜索框架
        search_frame = tk.LabelFrame(self.frame, text="交易记录搜索")
        search_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(search_frame, text="搜索:").grid(
            row=0, column=0, sticky="w", pady=5)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, pady=5, padx=5, sticky="ew")
        self.search_entry.bind('<KeyRelease>', self.search_transactions)

        search_frame.columnconfigure(1, weight=1)

        # 交易记录表格
        columns = ("日期", "类型", "类别", "金额", "备注")
        self.tree = ttk.Treeview(
            self.frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.pack(fill="both", expand=True, padx=20, pady=10)

    def update_budget(self):
        try:
            new_budget = float(self.budget_entry.get())
            if new_budget < 0:
                messagebox.showerror("错误", "预算不能为负数！")
                return

            budgets[0].amount = new_budget
            # 保存数据
            data_manager.save_data()
            self.update_display()
            messagebox.showinfo("成功", "预算更新成功！")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的预算金额！")

    def calculate_monthly_data(self):
        """计算月度数据"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_expense = 0
        monthly_income = 0

        for transaction in transactions:
            if transaction.date.startswith(current_month):
                if transaction.type == "支出":
                    monthly_expense += transaction.amount
                else:
                    monthly_income += transaction.amount

        return monthly_expense, monthly_income

    def update_display(self):
        """更新显示"""
        monthly_expense, monthly_income = self.calculate_monthly_data()
        budget = budgets[0].amount
        balance = budget - monthly_expense

        self.budget_label.config(text=f"预算: {budget:.2f}")
        self.expense_label.config(text=f"支出: {monthly_expense:.2f}")
        self.income_label.config(text=f"收入: {monthly_income:.2f}")

        # 根据余额设置颜色
        if balance >= 0:
            self.balance_label.config(text=f"余额: {balance:.2f}", fg="green")
        else:
            self.balance_label.config(text=f"超支: {-balance:.2f}", fg="red")

        # 更新表格
        self.search_transactions()

    def search_transactions(self, event=None):
        """搜索交易记录"""
        search_term = self.search_entry.get().lower()

        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 填充数据
        for transaction in reversed(transactions):  # 最新的在前面
            if (search_term in transaction.category.lower() or
                search_term in transaction.note.lower() or
                search_term in str(transaction.amount) or
                search_term in transaction.date or
                    search_term in transaction.type.lower()):

                self.tree.insert("", "end", values=(
                    transaction.date,
                    transaction.type,
                    transaction.category,
                    f"{transaction.amount:.2f}",
                    transaction.note
                ))

    def show(self):
        self.frame.pack(fill="both", expand=True)
        self.update_display()

    def hide(self):
        self.frame.pack_forget()
