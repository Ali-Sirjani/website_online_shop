var updateBtns = document.getElementsByClassName('update-cart')

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var action = this.dataset.action
        var quantityInput = document.getElementById('qty');
        var quantity =  quantityInput ? quantityInput.value : 1;

        console.log('productId', productId, 'action', action)

        console.log('User: ', user)
        updateUserOrder(productId, action, quantity)
    })
}
function updateUserOrder(productId, action, quantity) {
    console.log('user log in', quantity)

    var url = 'http://127.0.0.1:8000/cart/update-item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action, 'quantity': quantity})
    })


        .then((response) => {
            console.log('data')
            return response.json()
        })

        .then((data) => {
            console.log('data', data)
            location.reload()
        })

}
