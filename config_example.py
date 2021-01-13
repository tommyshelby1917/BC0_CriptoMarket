DBFILE='POSA_LA_RUTA_DE_LA_TEVA_DB_AQUI'

    form = RegisterForm(request.form)
    
    if request.method == 'POST':

        if form.validate():
            consulta('INSERT INTO users (password, email, fecha_alta) VALUES (?, ? ,? );', 
                    (
                        form.email_registre.data,
                        form.password_registre.data,
                        "ahora",
                    )
            )

            return redirect(url_for('/'))
        else:
            return render_template("registre.html", form=form)
            

    return render_template("registre.html", form=form)