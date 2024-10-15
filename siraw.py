from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Application, ContextTypes, MessageHandler
from telegram.ext.filters import TEXT, COMMAND

API_TOKEN = '7785764919:AAFWvAlVtpDYxFxTcg5ffPBVZkrU6xuyfA0'  # Replace with your bot token

# In-memory storage for demonstration purposes
employees = {}
attendance = {}
leave_requests = []
payroll = {}

# Function to show the main menu
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Add Employee", callback_data='add_employee')],
        [InlineKeyboardButton("List Employees", callback_data='list_employees')],
        [InlineKeyboardButton("Update Employee", callback_data='update_employee')],
        [InlineKeyboardButton("Delete Employee", callback_data='delete_employee')],
        [InlineKeyboardButton("Add Payroll", callback_data='add_payroll')],
        [InlineKeyboardButton("View Payroll", callback_data='view_payroll')],
        [InlineKeyboardButton("Mark Attendance", callback_data='mark_attendance')],
        [InlineKeyboardButton("Request Leave", callback_data='request_leave')],
        [InlineKeyboardButton("Help", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please choose an option:', reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome to the Employee Management Bot!")
    await show_main_menu(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Here are the available commands:\n"
        "1. Add Employee: Add a new employee.\n"
        "2. List Employees: View all employees.\n"
        "3. Update Employee: Change an employee's name.\n"
        "4. Delete Employee: Remove an employee.\n"
        "5. Add Payroll: Assign salary to an employee.\n"
        "6. View Payroll: Check salary records.\n"
        "7. Mark Attendance: Mark attendance for an employee.\n"
        "8. Request Leave: Submit a leave request."
    )
    await update.message.reply_text(help_text)
    await show_main_menu(update, context)

async def button_selection_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'add_employee':
        await query.edit_message_text("Please send the employee's name:")
        context.user_data['action'] = 'add_employee'
    elif query.data == 'list_employees':
        await list_employees(query)
    elif query.data == 'update_employee':
        await query.edit_message_text("Please send the employee ID to update:")
        context.user_data['action'] = 'update_employee'
    elif query.data == 'delete_employee':
        await query.edit_message_text("Please send the employee ID to delete:")
        context.user_data['action'] = 'delete_employee'
    elif query.data == 'add_payroll':
        await query.edit_message_text("Please send the employee ID and salary (format: ID,SALARY):")
        context.user_data['action'] = 'add_payroll'
    elif query.data == 'view_payroll':
        await view_payroll(query)
    elif query.data == 'mark_attendance':
        await query.edit_message_text("Please send the employee ID to mark attendance:")
        context.user_data['action'] = 'mark_attendance'
    elif query.data == 'request_leave':
        await query.edit_message_text("Please send the leave request details:")
        context.user_data['action'] = 'request_leave'
    elif query.data == 'help':
        await help_command(query.message, context)

# Function to handle adding an employee
async def add_employee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('action') == 'add_employee':
        name = update.message.text.strip()
        employee_id = len(employees) + 1  # Generate a new employee ID
        employees[employee_id] = {'name': name}
        await update.message.reply_text(f"Employee added: {name} (ID: {employee_id})")
        context.user_data.pop('action', None)  # Clear the action
        await show_main_menu(update, context)

# Function to list all employees
async def list_employees(query):
    if not employees:
        await query.edit_message_text("No employees found.")
    else:
        employee_list = '\n'.join([f"ID: {emp_id}, Name: {info['name']}" for emp_id, info in employees.items()])
        await query.edit_message_text(f"Employees:\n{employee_list}")
    await show_main_menu(query, query.message.chat.id)

# Function to handle updating an employee
async def update_employee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('action') == 'update_employee':
        try:
            employee_id = int(update.message.text.strip())
            if employee_id in employees:
                await update.message.reply_text(f"Updating employee ID: {employee_id}. Please send the new name:")
                context.user_data['update_employee_id'] = employee_id
            else:
                await update.message.reply_text(f"No employee found with ID: {employee_id}.")
        except ValueError:
            await update.message.reply_text("Please send a valid employee ID.")

# Function to handle the name update
async def handle_update_employee_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    employee_id = context.user_data.get('update_employee_id')
    if employee_id:
        employees[employee_id]['name'] = update.message.text.strip()
        await update.message.reply_text(f"Employee ID: {employee_id} updated to {update.message.text.strip()}.")
        context.user_data.pop('update_employee_id', None)  # Clear the stored ID
        context.user_data.pop('action', None)  # Clear the action
    else:
        await update.message.reply_text("No employee ID found for update.")
    await show_main_menu(update, context)

# Function to handle deleting an employee
async def delete_employee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('action') == 'delete_employee':
        try:
            employee_id = int(update.message.text.strip())
            if employee_id in employees:
                del employees[employee_id]
                await update.message.reply_text(f"Employee ID: {employee_id} has been deleted.")
            else:
                await update.message.reply_text(f"No employee found with ID: {employee_id}.")
        except ValueError:
            await update.message.reply_text("Please send a valid employee ID.")
        context.user_data.pop('action', None)  # Clear the action
    await show_main_menu(update, context)

# Function to handle adding payroll
async def add_payroll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('action') == 'add_payroll':
        try:
            input_data = update.message.text.split(',')
            employee_id = int(input_data[0].strip())
            salary = float(input_data[1].strip())
            
            if employee_id in employees:
                payroll[employee_id] = salary
                await update.message.reply_text(f"Payroll added for Employee ID: {employee_id} with Salary: {salary}.")
            else:
                await update.message.reply_text(f"No employee found with ID: {employee_id}.")
        except (ValueError, IndexError):
            await update.message.reply_text("Please send the data in the format: ID,SALARY.")
        context.user_data.pop('action', None)  # Clear the action
    
    await show_main_menu(update, context)

# Function to view payroll records
async def view_payroll(query):
    if not payroll:
        await query.edit_message_text("No payroll records found.")
    else:
        payroll_list = '\n'.join([f"ID: {emp_id}, Salary: {salary}" for emp_id, salary in payroll.items()])
        await query.edit_message_text(f"Payroll Records:\n{payroll_list}")
    await show_main_menu(query, query.message.chat.id)

# Function to mark attendance
async def mark_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('action') == 'mark_attendance':
        try:
            employee_id = int(update.message.text.strip())
            if employee_id in employees:
                attendance[employee_id] = True  # Mark attendance as True
                await update.message.reply_text(f"Attendance marked for employee ID: {employee_id}.")
            else:
                await update.message.reply_text(f"No employee found with ID: {employee_id}.")
        except ValueError:
            await update.message.reply_text("Please send a valid employee ID.")
        context.user_data.pop('action', None)  # Clear the action
    
    await show_main_menu(update, context)

# Function to request leave
async def request_leave(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('action') == 'request_leave':
        leave_request = update.message.text.strip()
        employee_id = context.user_data.get('employee_id')  # Assuming you store the employee ID somewhere
        if employee_id:
            leave_requests.append({'employee_id': employee_id, 'request': leave_request})
            await update.message.reply_text("Leave request submitted.")
        else:
            await update.message.reply_text("No employee ID found for leave request.")
        context.user_data.pop('action', None)  # Clear the action
    
    await show_main_menu(update, context)

def main():
    application = Application.builder().token(API_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_selection_handler))
    application.add_handler(MessageHandler(TEXT & ~COMMAND, add_employee))  # Assuming add_employee is also for text input
    application.add_handler(MessageHandler(TEXT & ~COMMAND, update_employee))  # Update employee
    application.add_handler(MessageHandler(TEXT & ~COMMAND, delete_employee))  # Delete employee
    application.add_handler(MessageHandler(TEXT & ~COMMAND, add_payroll))  # Add payroll
    application.add_handler(MessageHandler(TEXT & ~COMMAND, mark_attendance))  # Mark attendance
    application.add_handler(MessageHandler(TEXT & ~COMMAND, request_leave))  # Request leave
    application.add_handler(MessageHandler(TEXT & ~COMMAND, handle_update_employee_name))  # Handle updating name
    
    application.run_polling()

if __name__ == '__main__':
    main()
