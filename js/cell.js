/// <reference types="p5/global" />

// cell / conjunto

/* TODO: -arreglar texto al mover (que el texto siga la fisica de la cell y se centre, podemos tal vez hacer que se deforme tambien)
         -cambiar el cursor cuando estamos encima de la cell\
         - colision entre cells?? o que podamos hacer operaciones entre los conjuntos lanzando unos con otros?
         - A;ADIR ORDEN de interaccion, que se muestren por encima las ultimas con las que hemos interactuado
         - CREAR UPSET PLOT AL DARLE CLICK 
 */
class Cell {
    constructor(x, y, radius, col, name, count) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.color = col;
        this.name = name;
        this.count = count;

        // eventos
        this.isDragging = false;
        this.offsetX = 0;
        this.offsetY = 0;

        this.noiseTime = random(1000);


        // Fisicas ANIMACION STRETCH AL MOVER
        this.prevX = x; // Posiciones en el frame anterior
        this.prevY = y;
        this.stretchVelX = 0;  
        this.stretchVelY = 0;  
        this.physicsVelX = 0;  
        this.physicsVelY = 0;  
    }

    show() {
        // SE VE COMPLEJO PERO NO LO ES, SOLO ESTAMOS HACIENDO LA FIGURA DE LOS DOS CIRCULOS Y LA HACEMOS A MANO COGIENDO LOS VERTICES
        // PARA LUEGO PODER DEFORMAR EL CIRCULO A NUESTRO GUSTO

        // BORDE 
        noStroke()

        // borde mas oscuro que el color
        let darkColor = color(red(this.color) * 0.5, green(this.color) * 0.5, blue(this.color) * 0.5 );

        // vertices del relleno
        let innerVertices = [];

        fill(darkColor)

        //  noise para que el borde vibre
        beginShape();
        let time = this.noiseTime + frameCount * 0.004;
        for (let a = 0; a < TWO_PI; a += 0.06) {
            let noiseVal = noise(time + a * 0.4);
            let r = this.radius + map(noiseVal, 0, 1, -this.radius * 0.06, this.radius * 0.06)

            // FISICAS ARRASTRE
            let stretch = this.stretchVelX * cos(a) + this.stretchVelY * sin(a);
            stretch *= 1.3;
            r += stretch;

            vertex(this.x + r * cos(a), this.y + r * sin(a));

            //INTERIOR RELLENO
            let inner_r_base = this.radius * 0.85;
            let inner_r = inner_r_base + map(noiseVal, 0, 1, -inner_r_base * 0.06, inner_r_base * 0.06);
            inner_r += stretch;

            // Guardamos el vertice para dibujarlo despues
            innerVertices.push({
                x: this.x + inner_r * cos(a), 
                y: this.y + inner_r * sin(a)
            });

        }
        endShape(CLOSE);
        
        // Relleno
        fill(this.color);
        beginShape();
        for(let v of innerVertices) {
            vertex(v.x, v.y);
        }
        endShape(CLOSE);

        // Texto
        fill(0);
        textAlign(CENTER, CENTER);
        textSize(16);
        text(this.name + "\n" + this.count, this.x, this.y, );

    }

    update() {

        this.prevX = this.x;
        this.prevY = this.y;

        if(this.isDragging) {
            this.x = worldMouseX - this.offsetX;
            this.y = worldMouseY - this.offsetY;
        } else {
            this.x += this.physicsVelX;
            this.y += this.physicsVelY;

            this.physicsVelX *= 0.90; 
            this.physicsVelY *= 0.90;
        }

        //FISICAS  velocidad instantanea
        let instantVelX = this.x - this.prevX;
        let instantVelY = this.y - this.prevY;

        this.stretchVelX = lerp(this.stretchVelX, instantVelX, 0.1); 
        this.stretchVelY = lerp(this.stretchVelY, instantVelY, 0.1);

        
    }

    isMouseOver() {
        let d = dist(worldMouseX, worldMouseY, this.x, this.y);
        return d < this.radius;
    }

    //arrastre de la celula
    startDrag() {

        this.isDragging = true;
        this.offsetX = worldMouseX - this.x;
        this.offsetY = worldMouseY - this.y;

        this.physicsVelX = 0;
        this.physicsVelY = 0;
    }

    stopDrag() {
        this.isDragging = false;

        this.physicsVelX = this.stretchVelX;
        this.physicsVelY = this.stretchVelY;
    }

}