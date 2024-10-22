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
}