srchBox=document.getElementById('searchTxt');
srchBox.addEventListener('input',function(){
    
    let searchTerm= srchBox.value.toLowerCase();

    let note_cards=document.getElementsByClassName('noteCard');

    Array.from(note_cards).forEach(function(element){
        let note_title = element.getElementsByTagName("h5")[0].innerText.toLowerCase();
        let note_desc = element.getElementsByTagName("p")[0].innerText.toLowerCase();


        if(!note_title.includes(searchTerm) && !note_desc.includes(searchTerm))
        {
            element.style.display='none';
        }
        else
        {
            element.style.display='block';
        }

    })
    
})


         