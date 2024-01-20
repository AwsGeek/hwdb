page_number = 1
page_size = 5
sort_order = 'id'
sort_direction = 'asc'
search_phrase = ''

function updateTable() {
    console.log(page_size)
    url = users_url
    url = url.replaceAll("&amp;", "&")
    url = url.replace("PAGESIZE", page_size)
    url = url.replace("PAGENUMBER", page_number)
    url = url.replace("SORTORDER", sort_order)
    url = url.replace("SORTDIRECTION", sort_direction)
    url = url.replace("SEARCHPHRASE", search_phrase)
    $.ajax({
        type: "GET",
        url: url,
        dataType: "json",
        success: function(data){
            console.log(data)

            $('table.users tbody').find('tr.user').remove()
            $.each(data.user_list, function (index, value) {
                var tr = '<tr class="user">' +
                        '<td>' + value.id + '</td>' +
                        '<td><img src="' + value.image + '" class="object-fit-cover rounded-circle" width="26" height="26"></td>' +
                        '<td>' + value.name + '</td>' +
                        '<td>' + value.email + '</td>' + 
                        '<td>' + value.active + '</td>' + 
                        '<td>' + value.banned + '</td>' + 
                        '<td>' + value.last_login + '</td>' + 
                        '<td>' + value.last_activity + '</td>' + 
                        '<td><button type="button" class="btn btn-primary editUserOpen" data-user_id="' + value.id  + '">Edit</button></td>' + 
                        '</tr>';
                $('table.users tbody').append(tr)
            });
            $('ul.pagination').find('li').remove()
            if (data.total_pages) {

                num_links = Math.min(Math.floor((data.total_pages*2-1)/2), 7)
                num_links = Math.min(data.total_pages, 7)

                max_page = data.current_page+Math.floor(num_links/2)
                min_page = data.current_page-Math.floor(num_links/2)
                if (min_page < 1) {
                    max_page = num_links
                    min_page = 1
                }

                if (max_page > data.total_pages) {
                    min_page = Math.max(1, data.total_pages-num_links+1)
                    max_page = data.total_pages
                }

                $('ul.pagination').append('<li class="page-item"><a class="page-link" data-page="' + (Math.max(data.current_page-1, 1)) + '" href="javascript:void(0)">&lt;</a></li>')              
                for (let idx = min_page; idx <= max_page; idx++) {
                    if (idx == data.current_page) {
                    $('ul.pagination').append('<li class="page-item active"><a class="page-link" data-page="' + idx + '" href="javascript:void(0)">' + idx + '</a></li>')              
                    } else {
                    $('ul.pagination').append('<li class="page-item"><a class="page-link" data-page="' + idx + '" href="javascript:void(0)">' + idx + '</a></li>')              
                    }
                }
                $('ul.pagination').append('<li class="page-item"><a class="page-link" data-page="' + (Math.min(data.current_page+1, data.total_pages)) + '" href="javascript:void(0)">&gt;</a></li>')               
                $('ul.displaying').html('<span>Showing ' + data.user_list.length + ' of <strong>' + data.total_users + ' total users</strong></span>')
                $('ul.dropdown button').text(page_size)

            }

            $('a.page-link').on('click', function (event) {
                page_number = $(this).attr("data-page");
                updateTable()
            });
            
            $('button.editUserOpen').on('click',function(event) {
                user_id = $(this).data("user_id");

                var modal = $('#editUserModal')
                $.ajax({
                    type: "GET",
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    url: "/api/users/" + user_id,
                    success: function(data){
                        console.log(data)
        
                        modal.find('#user_id').val(data.id)
                        modal.find('#image').attr("src", data.image)
                        modal.find('#name').val(data.name)
                        modal.find('#email').val(data.email)

                        modal.modal('show');


                    },
                    error: function(errMsg) {
                        console.log(errMsg);
                        $('#exampleModal'). modal('hide')
                    }
                });       

            });  
            
        },
        error: function(errMsg) {
            console.log(errMsg);
        }
    });
    }

$(document).ready(function(){

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });


    $('button.editUserClose').on('click',function(event) {
        modal = $('#editUserModal')
        modal.find('#image').attr("src", "")
        modal.find('#name').val("")
        modal.find('#email').val("")

        modal.modal('hide');
    })

    $('button#editUserSave').on('click',function(event) {
        modal = $('#editUserModal')
        id = modal.find('#user_id').val()
        name = modal.find('#user_id').val()
        email = modal.find('#email').val()
        console.log(id,name,email)

        $.ajax({
            type: "PUT",
            contentType: "application/json; charset=utf-8",
            data: {id: id, name: name, email:email},
            dataType: "json",
            url: "/api/users/" + id,
            success: function(data){
                console.log(data)

                modal.find('#image').attr("src", data.image)
                modal.find('#name').val(data.name)
                modal.find('#email').val(data.email)

                modal.modal('show');


            },
            error: function(errMsg) {
                console.log(errMsg);
                $('#exampleModal'). modal('hide')
            }
        });       

    });  

    $('th.sortable').on('click', function (event) {
        event.preventDefault();

        sort_order = $(this).attr('sort-order')
        if ($(this).is(".sorted")) {
        sort_direction = $(this).attr('sort-direction')
        sort_direction = sort_direction == "asc" ? "desc" : "asc"
        }
        $(this).attr('sort-direction', sort_direction)

        $('th.sortable').removeClass('sorted')
        $(this).addClass('sorted')

        updateTable()
    });
    
    $('#search_phrase').on('search', function (event) {
        sf = $('#search_phrase').val();
        
        if (sf == search_phrase) {
            return
        }

        search_phrase = sf
        updateTable()
    });

    $('button#search_button').on('click', function (event) {
        event.preventDefault();
        sf = $('#search_phrase').val();
        
        if (sf == search_phrase) {
            return
        }

        search_phrase = sf
        updateTable()
    });


    $('a.dropdown-item').on('click', function (event) {

        new_page_size = $(this).attr("data-page_size");
        if (new_page_size == page_size) {
        return
        }
        page_size = new_page_size
        page_number = 1
        $('a.dropdown-item').removeClass('active')
        $(this).addClass('active')
        
        updateTable()
    });

    updateTable()
})
