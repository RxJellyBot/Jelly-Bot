let selectedTags = [];

let searchLock = false;

function searchTag() {
    if (!searchLock) {
        searchLock = true;

        const txt = $("input#arTagKeyword").val();

        if (txt.includes(tagSplitter) || txt.length === 0) {
            $("div#tagSearchErr").tooltip('enable').tooltip('show').tooltip('disable');
            searchLock = false;
            return;
        }

        searchTagsByPopularity(txt,
            tag_name_arr => {
                if (!tag_name_arr.includes(txt)) {
                    attachTagButton(txt);
                }

                tag_name_arr.forEach(tag_name => attachTagButton(tag_name));
            },
            () => attachTagButton(txt),
            clearSearchResults
        );
        searchLock = false;
    }
}

function attachTagButton(txt) {
    if (txt) {
        $("div#arTagSearchResult").append(generateTagButtonDOM(txt, event => addToSelectedTags($(event.target).text())));
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
    return generateTagButtonDOM(txt, event => {
        $(event.target).parent().remove();
        selectedTags = selectedTags.filter(e => e !== txt);
    })
}

function generateTagButtonDOM(txt, btnOnClick = null) {
    const elem = $.parseHTML(`<div class="d-inline"><button type="button" class="btn btn-outline-success mb-1 ar-tag">${txt}</button>&nbsp;</div>`);

    if (btnOnClick) {
        elem.forEach(element => $(element).find("button").click(btnOnClick));
    }
    return elem;
}

function getTagsByPopularity(onFound, onNotFound) {
    searchTagsByPopularity("", onFound, onNotFound, () => {
    });
}

$(document).ready(() => {
    getTagsByPopularity(
        tag_name_arr => {
            $("div#arTagPopMsg").addClass("d-none");

            tag_name_arr
                .forEach(tag_name =>
                    $("div#arTagPop").append(
                        generateTagButtonDOM(tag_name, event => addToSelectedTags($(event.target).text()))
                    )
                )
        },
        () => $("div#arTagPopMsg").removeClass("d-none"));
    $("button#arTagSearch").click(searchTag);

    $("input#arTagKeyword").keyup(e => {
        if (e.which === 13) {
            searchTag();
            return false;
        }
        return true;
    });
});