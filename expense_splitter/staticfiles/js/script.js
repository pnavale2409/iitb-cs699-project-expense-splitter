// JavaScript code for handling enhanced expense management and calculation

const expensesList = document.getElementById('expenses-list');
const expenseNameInput = document.getElementById('expense-name');
const expenseAmountInput = document.getElementById('expense-amount');
const payerInput = document.getElementById('payer');
const addExpenseButton = document.getElementById('add-expense');
const summaryDiv = document.getElementById('summary');
const breakdownDiv = document.getElementById('breakdown');

// Initialize an array to store expenses
let expenses = [];
let participants = new Set();

// Function to add a new expense
function addExpense() {
    const name = expenseNameInput.value;
    const amount = parseFloat(expenseAmountInput.value);
    const payer = payerInput.value;

    if (name && !isNaN(amount) && payer) {
        const expense = { name, amount, payer };
        expenses.push(expense);
        participants.add(payer);

        // Create a new list item to display the expense
        const listItem = document.createElement('li');
        listItem.innerHTML = `<strong>${name}</strong> ($${amount.toFixed(2)} paid by ${payer})`;
        expensesList.appendChild(listItem);

        // Clear input fields
        expenseNameInput.value = '';
        expenseAmountInput.value = '';
        payerInput.value = '';

        // Update the summary and breakdown
        updateSummary();
        updateBreakdown();
    }
}

// Function to update the expense summary
function updateSummary() {
    const totalExpense = expenses.reduce((total, expense) => total + expense.amount, 0);
    const averageExpense = totalExpense / participants.size;

    summaryDiv.innerHTML = `
        Total Expense: $${totalExpense.toFixed(2)}<br>
        Average Expense per Participant: $${averageExpense.toFixed(2)}
    `;
}

// Function to update the detailed expense breakdown
function updateBreakdown() {
    const balances = {};

    for (const participant of participants) {
        balances[participant] = 0;
    }

    for (const expense of expenses) {
        balances[expense.payer] += expense.amount;
    }

    breakdownDiv.innerHTML = '<h3>Expense Breakdown:</h3>';

    for (const participant of participants) {
        breakdownDiv.innerHTML += `<p>${participant} owes:</p>`;

        for (const debtor of participants) {
            if (participant !== debtor) {
                const amountOwed = (balances[debtor] - balances[participant]).toFixed(2);
                breakdownDiv.innerHTML += `<p>${debtor}: $${amountOwed}</p>`;
            }
        }
    }
}

// Event listener for adding an expense
addExpenseButton.addEventListener('click', addExpense);
