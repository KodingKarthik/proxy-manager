import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useAuth } from '../contexts/AuthContext';
import { Button, Input } from '@proxy-manager/ui';
import { registerSchema, type RegisterFormData } from '../schemas/auth.schema';

const Register = () => {
  const { register: registerUser } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setError(null);
      setIsLoading(true);
      await registerUser(data.username, data.email, data.password);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else if (typeof err === 'object' && err !== null && 'response' in err) {
        const axiosError = err as { response?: { data?: { detail?: string | Array<{ msg: string }> } } };
        const detail = axiosError.response?.data?.detail;
        if (Array.isArray(detail)) {
          setError(detail.map((d) => d.msg).join(', '));
        } else if (typeof detail === 'string') {
          setError(detail);
        } else {
          setError('Registration failed');
        }
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg px-4">
      <div className="max-w-md w-full card">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-neon-cyan mb-2">Create Account</h1>
          <p className="text-muted">Sign up for a new account</p>
        </div>

        {error && (
          <div
            className="mb-4 p-3 bg-neon-magenta bg-opacity-20 border border-neon-magenta rounded-lg text-neon-magenta text-sm"
            role="alert"
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Username"
            type="text"
            {...register('username')}
            error={errors.username?.message}
            autoComplete="username"
            autoFocus
          />

          <Input
            label="Email"
            type="email"
            {...register('email')}
            error={errors.email?.message}
            autoComplete="email"
          />

          <Input
            label="Password"
            type="password"
            {...register('password')}
            error={errors.password?.message}
            autoComplete="new-password"
          />

          <Input
            label="Confirm Password"
            type="password"
            {...register('confirmPassword')}
            error={errors.confirmPassword?.message}
            autoComplete="new-password"
          />

          <Button type="submit" className="w-full" isLoading={isLoading}>
            Sign Up
          </Button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-muted">
            Already have an account?{' '}
            <Link to="/login" className="text-neon-cyan hover:text-accent font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;

