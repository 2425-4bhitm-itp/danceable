package at.leonding.htl.features.analyze.fourier;

public class Complex {
    double real;
    double imaginary;
    double abs;

    public Complex(double real, double imaginary) {
        this.real = real;
        this.imaginary = imaginary;
        this.abs = Math.sqrt(real * real + imaginary * imaginary);
    }

    public double getAbs() {
        return this.abs;
    }

    public Complex add(Complex other) {
        return new Complex(this.real + other.real, this.imaginary + other.imaginary);
    }

    public Complex subtract(Complex other) {
        return new Complex(this.real - other.real, this.imaginary - other.imaginary);
    }

    public Complex multiply(Complex other) {
        double realPart = this.real * other.real - this.imaginary * other.imaginary;
        double imaginaryPart = this.real * other.imaginary + this.imaginary * other.real;
        return new Complex(realPart, imaginaryPart);
    }
}