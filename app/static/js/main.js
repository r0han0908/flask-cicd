// SocialConnect JavaScript functionality

$(document).ready(function() {
    // Like/unlike functionality
    $('.like-btn').click(function(e) {
        e.preventDefault();
        const button = $(this);
        const postId = button.data('post-id');
        const liked = button.data('liked');
        
        // Add loading state
        const originalContent = button.html();
        button.html('<span class="loading"></span>');
        button.prop('disabled', true);
        
        $.post(`/posts/${postId}/like`, {}, function(data) {
            // Update button state
            const icon = button.find('i');
            const likeCount = button.find('.like-count');
            
            if (data.liked) {
                button.addClass('liked');
                button.data('liked', true);
                icon.removeClass('far').addClass('fas');
            } else {
                button.removeClass('liked');
                button.data('liked', false);
                icon.removeClass('fas').addClass('far');
            }
            
            likeCount.text(data.like_count);
        }).fail(function() {
            alert('Error updating like status. Please try again.');
        }).always(function() {
            // Remove loading state
            button.html(originalContent);
            button.prop('disabled', false);
        });
    });
    
    // Follow/unfollow functionality
    $('.follow-btn').click(function(e) {
        e.preventDefault();
        const button = $(this);
        const username = button.data('username');
        const following = button.data('following');
        
        // Add loading state
        const originalContent = button.html();
        button.html('<span class="loading"></span> Loading...');
        button.prop('disabled', true);
        
        const url = following ? `/users/unfollow/${username}` : `/users/follow/${username}`;
        
        $.post(url, {}, function(data) {
            if (data.following) {
                button.removeClass('btn-primary').addClass('btn-outline-secondary');
                button.html('<i class="fas fa-user-minus"></i> Unfollow');
                button.data('following', true);
            } else {
                button.removeClass('btn-outline-secondary').addClass('btn-primary');
                button.html('<i class="fas fa-user-plus"></i> Follow');
                button.data('following', false);
            }
            
            // Update follower count if element exists
            $('.follower-count').text(data.follower_count);
        }).fail(function() {
            alert('Error updating follow status. Please try again.');
            button.html(originalContent);
        }).always(function() {
            button.prop('disabled', false);
        });
    });
    
    // Auto-resize textareas
    $('textarea').each(function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    }).on('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
    
    // Image preview for file uploads
    $('input[type="file"]').change(function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                let preview = $(e.target).siblings('.image-preview');
                if (preview.length === 0) {
                    preview = $('<div class="image-preview mt-2"></div>');
                    $(e.target).after(preview);
                }
                preview.html(`<img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px;">`);
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').click(function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').animate({
                scrollTop: target.offset().top - 100
            }, 500);
        }
    });
    
    // Auto-hide alerts after 5 seconds
    $('.alert').each(function() {
        const alert = $(this);
        setTimeout(function() {
            alert.fadeOut();
        }, 5000);
    });
    
    // Confirm delete actions
    $('.delete-btn').click(function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
    
    // Character counter for textareas with max length
    $('textarea[maxlength]').each(function() {
        const textarea = $(this);
        const maxLength = textarea.attr('maxlength');
        const counter = $(`<div class="character-counter text-muted small text-end mt-1">${textarea.val().length}/${maxLength}</div>`);
        textarea.after(counter);
        
        textarea.on('input', function() {
            const currentLength = textarea.val().length;
            counter.text(`${currentLength}/${maxLength}`);
            
            if (currentLength > maxLength * 0.9) {
                counter.addClass('text-warning');
            } else {
                counter.removeClass('text-warning');
            }
            
            if (currentLength >= maxLength) {
                counter.addClass('text-danger');
            } else {
                counter.removeClass('text-danger');
            }
        });
    });
    
    // Lazy loading for images
    $('img[data-src]').each(function() {
        const img = $(this);
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = $(entry.target);
                    img.attr('src', img.data('src'));
                    img.removeAttr('data-src');
                    observer.unobserve(entry.target);
                }
            });
        });
        observer.observe(this);
    });
});

// Utility functions
function showToast(message, type = 'info') {
    const toast = $(`
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `);
    
    $('.toast-container').append(toast);
    const bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

function formatTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)} months ago`;
    return `${Math.floor(diffInSeconds / 31536000)} years ago`;
}
