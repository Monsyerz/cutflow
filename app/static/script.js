const addButton = document.getElementById('add-cut');
const cutsContainer = document.getElementById('cuts-container');

addButton.addEventListener('click', function () {

    const cutDiv = document.createElement('div');

    cutDiv.classList.add('cut-row');

    cutDiv.innerHTML = `
        <div class="input-box">
            <label>Cut Length</label>
            <input
                type="number"
                name="cut_length"
                step="0.01"
                min="0.01"
                required>
        </div>

        <div class="input-box">
            <label>Quantity</label>
            <input
                type="number"
                name="quantity"
                step="1"
                min="1"
                required>
        </div>

        <button type="button" class="remove-cut">
            Remove
        </button>
    `;

    cutsContainer.appendChild(cutDiv);

    const removeButton = cutDiv.querySelector('.remove-cut');

    removeButton.addEventListener('click', function () {
        cutsContainer.removeChild(cutDiv);
    });

});