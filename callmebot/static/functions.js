
// receives a parent and a /posts response and renders posts HTML

export function renderPosts(parent, response, displayMode) { 
    for (var i = 0; i < response.posts.length; i++) {
        if (displayMode == 'columns') {
            // this template fits into a row div
            if (i % 3 == 0) {
                var ROW = document.createElement('div')
                ROW.className = 'row justify-content-start'
                parent.appendChild(ROW)
            }
            var card_template = document.createElement('div')
            card_template.innerHTML = `<div class="col-12 col-md-6 col-lg-4">${response.posts[i].html}</div>`
            
            // make card a bit smaller for profile page
            var card_container = card_template.getElementsByClassName('post-container')[0]
            card_container.style.width = '20rem';

            var card_img = card_template.getElementsByTagName('img')[0]
            card_img.style.maxHeight = '20rem';
            
            console.log(card_container)
            console.log(card_img)
            
            ROW.appendChild(card_template)

        } else if (displayMode == 'rows') {
            var card_template = response.posts[i].html
            parent.insertAdjacentHTML('beforeend', card_template)
            parent.appendChild(document.createElement("br"))
        }

        
    }
    addLikeListeners(parent)
}

function addLikeListeners(parent) {
    const like_btns = parent.getElementsByClassName('like-btn')
    for (var i = 0; i < like_btns.length; i++) {
        const post_container = like_btns[i].closest('.post-container')
        const post_id = post_container.getAttribute('data-post-id')
        const like_counter = post_container.getElementsByClassName('like-count')[0]

        like_btns[i].addEventListener('click', function(event) {
            $.ajax({
                url: `/like/${post_id}`,
                type: 'POST',
                success: function(response) {
                    // change like counter span
                    like_counter.innerHTML = response.likeCount
                }
            })
        })
    }
}