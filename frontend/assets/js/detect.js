function send() {

    $('html,body').animate({ scrollTop: $("#showtime").offset().top }, 'slow');

    var photo_src = document.getElementById("formFile_src").files[0];

    if(photo_src === undefined){
        $('#modal-title').text('Not so fast!');
        $('#modal-text').text('Please, choose an input image.');
        $('#myModal').modal('show');
        return;
    }

    var data = new FormData();

    data.append("file", photo_src);

    wi = document.getElementById('wi').value;
    ni = document.getElementById('ni').value;
    mi= document.getElementById('mi').value;

    $(document).ajaxStart(function () {
        $('#loader').show();
        $('#result_img').attr('style', 'display:none !important');
    });

    $(document).ajaxStop(function () {
        $('#loader').hide();
    });

    $.ajax({
        type: 'POST',
        url: '/read_watermark?' + $.param({'Wi': wi, 'ni': ni, 'mi': mi }),
        cache: false,
        contentType: false,
        processData: false,
        data: data,
        success: function (result) {
            console.log(result);
            var parent = document.getElementById('result_container');
            var result_card = document.getElementById("result_card");

            if (result_card != null) {
                parent.removeChild(result_card);
            }

            var result_card = document.createElement('div');
            result_card.id = "result_card";
            result_card.setAttribute("data-aos", "fade-bottom");
            result_card.style.marginTop = "5%";
            result_card.style.marginBottom = "5%";
            result_card.style.float = "none";
            result_card_class = result['is_watermarked'] ? 'card text-white bg-success' : 'card text-white bg-danger';
            result_card.className = result_card_class

            var result_card_body = document.createElement('div');
            result_card_body.className = "card-body";

            var result_card_body_title = document.createElement('p');
            result_card_body_title.style = 'font-size:1.5em;'
            result_card_body_title.className = "card-title"
            result_card_body_title.textContent = result['is_watermarked'] ? 'WATERMARK DETECTED' : 'NO WATERMARK DETECTED';
            result_card_body.append(result_card_body_title)

            var result_card_body_text = document.createElement('p');
            result_card_body_text.className = "card-text"
            result_card_body_text.textContent = result['is_watermarked'] ? 
                'The provided image contains the specified watermark at the specified location.' : 
                'The provided image does not contain the specified watermark at the specified location.';
            result_card_body.append(result_card_body_text)
            result_card.append(result_card_body)
            parent.append(result_card)

        },
        error: function (err) {
            // console.log(err);
            $('#modal-title').text('Oh no :(');
            $("#modal-text").text(err.responseJSON['detail']);
            $('#myModal').modal('show');
        }
    })
}


function sendUrl(valid_src) {

    valid = valid_src

    if (!valid) {
        $('#modal-title').text('Something Went Wrong :(')
        $("#modal-text").text("Make sure that you entered valid image URLs and try again.")
        $('#myModal').modal('show');
        return;
    }

    $(document).ajaxStart(function () {
        $('#loader').show();
        $('#result_img').attr('style', 'display:none !important');
    });

    $(document).ajaxStop(function () {
        $('#loader').hide();
    });

    wi = document.getElementById('wi').value;
    ni = document.getElementById('ni').value;
    mi= document.getElementById('mi').value;

    $.ajax({
        type: 'GET',
        url: '/read_watermark',
        cache: false,
        contentType: false,
        processData: false,
        data: $.param({ 'url': photo_src_url,
                        'Wi': wi,
                        'ni': ni,
                        'mi': mi }),
        success: function (result) {
            console.log(result);
            parent = document.getElementById('result_container');
            var result_card = document.getElementById("result_card");

            if (result_card != null) {
                parent.removeChild(result_card);
            }

            var result_card = document.createElement('div');
            result_card.id = "result_card";
            result_card.setAttribute("data-aos", "fade-bottom");
            result_card.style.marginTop = "5%";
            result_card.style.marginBottom = "5%";
            result_card.style.float = "none";
            result_card_class = result['is_watermarked'] ? 'card text-white bg-success' : 'card text-white bg-danger';
            result_card.className = result_card_class

            var result_card_body = document.createElement('div');
            result_card_body.className = "card-body";

            var result_card_body_title = document.createElement('p');
            result_card_body_title.style = 'font-size:1.5em;'
            result_card_body_title.className = "card-title"
            result_card_body_title.textContent = result['is_watermarked'] ? 'WATERMARK DETECTED' : 'NO WATERMARK DETECTED';
            result_card_body.append(result_card_body_title)

            var result_card_body_text = document.createElement('p');
            result_card_body_text.className = "card-text"
            result_card_body_text.textContent = result['is_watermarked'] ? 
                'The provided image contains the specified watermark at the specified location.' : 
                'The provided image does not contain the specified watermark at the specified location.';
            result_card_body.append(result_card_body_text)
            result_card.append(result_card_body)
            parent.append(result_card)

        },
        error: function (err) {
            
            $('#modal-title').text('Oh no :(');
            $("#modal-text").text(err.responseJSON['detail']);
            $('#myModal').modal('show');
        }
    })
}