function showDetails(){
    movies =document.querySelectorAll(".movie")
movies.forEach((movie)=>{
    movie.addEventListener("click",(e)=>{
        e.target.classList.add("rotate")
        setTimeout(()=>{
            movies.forEach(mov=>{
                mov.style.display= "none"
            })
            e.target.parentNode.style.display = "none"
            e.target.parentNode.nextElementSibling.style.display = "flex"

        },1000)
    })

})

}
function showMoviesList(e){
     movies =document.querySelectorAll(".movie")
     movie_details =document.querySelectorAll(".movie-details")
    movies.forEach(movie=>{
        movie.style.display = "flex"
    })
    movie_details.forEach(detail=>{
        detail.style.display ="none"
    })




}

