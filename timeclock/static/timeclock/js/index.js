let startDate = document.getElementById('start');
let endDate = document.getElementById('end');

startDate.addEventListener('click', () => {
    startDate.showPicker();
})

endDate.addEventListener('click', () => {
    endDate.showPicker();
})