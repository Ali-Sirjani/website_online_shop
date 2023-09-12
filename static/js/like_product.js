var likeBtns = document.getElementsByClassName('like-product')

for (var i = 0; i < likeBtns.length; i++) {
    likeBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product

        likeProduct(productId)
    })
}
function likeProduct(productId) {
    var url = 'http://127.0.0.1:8000/products/favorite/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId})
    })


        .then((response) => {
            console.log('data')
            return response.json()
        })

        .then((data) => {
            console.log('data', )

            if(data['authenticated'] === false){
                window.location.href = data['login']
            }
            else{
                location.reload()
            }

        })
}

