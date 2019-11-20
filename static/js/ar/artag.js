let selectedTags = [];

let searchLock = false;

// OPTIMIZE: Get tag's Object ID with the name during search and send oid back only

function searchTag() {
    if (!searchLock) {
        searchLock = true;

        let txt = $("input#arTagKeyword").val();

        if (txt.includes(tagSplittor) || txt.length === 0) {
            $("div#tagSearchErr").tooltip('enable').tooltip('show').tooltip('disable');
            searchLock = false;
            return;
        }

        searchTagsByPopularity(txt,
            function (tag_name_arr) {
                if (!tag_name_arr.includes(txt)) {
                    attachTagButton(txt);
                }

                tag_name_arr.forEach(function (tag_name) {
                    attachTagButton(tag_name);
                });
            },
            function () {
                attachTagButton(txt);
            },
            clearSearchResults
        );
        searchLock = false;
    }
}

function attachTagButton(txt) {
    if (txt) {
        $("div#arTagSearchResult").append(generateTagButtonDOM(txt, function (event) {
            addToSelectedTags($(event.target).text());
        }));
    }
}

function clearSearchResults() {
    $("div#arTagSearchResult").html("");
}

function addToSelectedTags(txt) {
    if (!selectedTags.includes(txt)) {
        $("div#arTagSelected").append(generatTagBOMSelfDestruct(txt));
        selectedTags.push(txt);
    }
    $("div#arTagSelectMsg").toggleClass("d-none", selectedTags.length !== 0);
}

function generatTagBOMSelfDestruct(txt) {
    return generateTagButtonDOM(txt, function (event) {
        $(event.target).parent().remove();
        selectedTags = selectedTags.filter(e => e !== txt);
    })
}

function generateTagButtonDOM(txt, btnOnClick = null) {
    let elem = $.parseHTML(`<div class="d-inline"><button type="button" class="btn btn-outline-success mb-1 ar-tag">${txt}</button>&nbsp;</div>`);

    if (btnOnClick) {
        elem.forEach(function (element) {
            $(element).find("button").click(btnOnClick);
        });
    }
    return elem;
}

function getTagsByPopularity(onFound, onNotFound) {
    searchTagsByPopularity("", onFound, onNotFound, function () {
    });
}

$(document).ready(function () {
    getTagsByPopularity(
        function (tag_name_arr) {
            $("div#arTagPopMsg").addClass("d-none");

            tag_name_arr.forEach(function (tag_name) {
                $("div#arTagPop").append(generateTagButtonDOM(tag_name, function (event) {
                    addToSelectedTags($(event.target).text());
                }));
            })
        },
        function () {
            $("div#arTagPopMsg").removeClass("d-none");
        });
    $("button#arTagSearch").click(searchTag);

    $("input#arTagKeyword").keyup(function (e) {
        if (e.which === 13) {
            searchTag();
            return false;
        }
    });
});