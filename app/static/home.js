import {renderPosts} from './functions.js'

$(document).ready(function(){
    $.ajax({
        url: '/posts',
        type: 'GET',
        success: function(response) {
            const POSTS = document.getElementById('posts');
            renderPosts(POSTS, response, 'rows')
        }
    })
})