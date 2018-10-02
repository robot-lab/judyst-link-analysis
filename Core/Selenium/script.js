function OpenPage(pageNum)
{
    var theForm = document.forms['aspnetForm'];
    if (!theForm) {
    theForm = document.aspnetForm;
    }
    function __doPostBack(eventTarget, eventArgument) {
    if (!theForm.onsubmit || (theForm.onsubmit() != false)) {
    theForm.__EVENTTARGET.value = eventTarget;
    theForm.__EVENTARGUMENT.value = eventArgument;
    theForm.submit();
    }
    }
    __doPostBack('ctl00$m$g_8da72b0e_36c3_43d7_9458_469b90467bbc$gView','Page$' + pageNum)
}
OpenPage(