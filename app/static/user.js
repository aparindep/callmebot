import {renderPosts} from './functions.js'

$(document).ready(function(){
    const URL = document.location.href
    var currentUser = URL.split('/').pop()
    $.ajax({
        url: `/posts/${currentUser}`,
        type: 'GET',
        success: function(response) {
            const POSTS = document.getElementById('posts');
            renderPosts(POSTS, response, 'columns')
        }
    })
})