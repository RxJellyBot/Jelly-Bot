function generateAlert(level, message) {
    return $("div.gen-alert").append(`<div class="row"><div class="alert alert-${level} alert-dismissible col fade show" role="alert">
                ${message}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span> 
                </button>
            </div></div>`.replace(" ", ""))
}