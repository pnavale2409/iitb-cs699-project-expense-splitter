// JavaScript code for handling expense management and calculation

const expensesList = document.getElementById('expenses-list');
const expenseNameInput = document.getElementById('expense-name');
const expenseAmountInput = document.getElementById('expense-amount');
const addExpenseButton = document.getElementById('add-expense');
const summaryDiv = document.getElementById('summary');

// Initialize an array to store expenses
let expenses = [];

// Function to add a new expense
function addExpense() {
    const name = expenseNameInput.value;
    const amount = parseFloat(expenseAmountInput.value);

    if (name && !isNaN(amount)) {
        const expense = { name, amount };
        expenses.push(expense);

        // Create a new list item to display the expense
        const listItem = document.createElement('li');
        listItem.innerHTML = `<strong>${name}</strong>: $${amount.toFixed(2)}`;
        expensesList.appendChild(listItem);

        // Clear input fields
        expenseNameInput.value = '';
        expenseAmountInput.value = '';

        // Update the summary
        updateSummary();
    }
}

// Function to update the expense summary
function updateSummary() {
    const totalExpense = expenses.reduce((total, expense) => total + expense.amount, 0);
    const averageExpense = totalExpense / expenses.length;

    summaryDiv.innerHTML = `
        Total Expense: $${totalExpense.toFixed(2}<br>
        Average Expense: $${averageExpense.toFixed(2}
    `;
}

// Event listener for adding an expense
addExpenseButton.addEventListener('click', addExpense);
