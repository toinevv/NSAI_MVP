import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Icons } from '../components/ui/icons';
import { Toaster, toast } from 'sonner';

const AuthPage = () => {
  const navigate = useNavigate();
  const { signIn, signUp, googleSignIn } = useAuth();
  
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [companyName, setCompanyName] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isRegisterMode) {
        // Register flow
        const [firstName, lastName] = fullName.split(' ');
        
        const { error } = await signUp(email, password, {
          full_name: fullName,
          company_name: companyName,
          first_name: firstName || '',
          last_name: lastName || '',
        });

        if (error) {
          throw error;
        } else {
          toast.success('Account created! Please check your email to confirm your account.');
        }
      } else {
        // Login flow
        const { error } = await signIn(email, password);
        
        if (error) {
          throw error;
        } else {
          toast.success('Signed in successfully');
          navigate('/dashboard');
        }
      }
    } catch (error: any) {
      toast.error(error.message || (isRegisterMode 
        ? 'Error creating account' 
        : 'Invalid email or password'
      ));
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="w-full min-h-screen flex flex-col lg:flex-row font-sans">
      <Toaster position="top-right" />
      
      {/* Left side - login form */}
      <div className="flex-1 p-6 md:p-10 flex flex-col bg-nsai-white animate-fade-in">
        <div className="mb-10">
          <h1 className="text-2xl font-bold">
            NewSystem<span className="text-nsai-teal">.AI</span>
          </h1>
        </div>
        
        <div className="flex-1 flex flex-col justify-center max-w-md mx-auto w-full animate-slide-in">
          
          <p className="text-nsai-gray mb-8 text-base leading-relaxed">
            NewSystem.AI is your gateway to industry-leading process mining & AI technology for logistics warehouses.
          </p>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {isRegisterMode && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="fullName" className="text-sm font-medium">
                    Full Name
                  </Label>
                  <Input
                    id="fullName"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required={isRegisterMode}
                    className="w-full p-3 border border-nsai-gray-light rounded-md text-base input-hover"
                    placeholder="John Doe"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="companyName" className="text-sm font-medium">
                    Company Name
                  </Label>
                  <Input
                    id="companyName"
                    type="text"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    required={isRegisterMode}
                    className="w-full p-3 border border-nsai-gray-light rounded-md text-base input-hover"
                    placeholder="Acme Logistics"
                  />
                </div>
              </>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">
                Your work/business email
              </Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full p-3 border border-nsai-gray-light rounded-md text-base input-hover"
                placeholder="name@company.com"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full p-3 border border-nsai-gray-light rounded-md text-base input-hover"
                placeholder="••••••••"
              />
            </div>
            
            <div className="text-sm text-nsai-gray">
              By submitting this form, you confirm that you agree to the storing and processing of your personal data as described in our <a href="#" className="text-nsai-teal hover:underline">Privacy Notice</a>
            </div>
            
            <div className="space-y-4">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 bg-nsai-teal text-white border-none rounded-full text-base font-medium hover:opacity-90 transition-all duration-200 ease-in-out btn-hover"
              >
                {isLoading ? (
                  <>
                    <Icons.spinner className="mr-2 h-4 w-4 animate-spin" />
                    {isRegisterMode ? "Creating Account..." : "Signing in..."}
                  </>
                ) : (
                  isRegisterMode ? "Create Account" : "Sign In"
                )}
              </Button>
              
              <div className="relative flex items-center">
                <div className="flex-grow border-t border-nsai-gray-light"></div>
                <span className="flex-shrink mx-4 text-nsai-gray text-sm">or</span>
                <div className="flex-grow border-t border-nsai-gray-light"></div>
              </div>
              
              <Button
                type="button"
                variant="outline"
                onClick={googleSignIn}
                className="w-full py-3 flex items-center justify-center gap-2 rounded-full border border-nsai-gray-light text-base btn-hover"
              >
                <Icons.google className="h-5 w-5" />
                Continue with Google
              </Button>
            </div>
            
            <div className="text-center">
              <Button 
                type="button"
                variant="link"
                onClick={() => setIsRegisterMode(!isRegisterMode)}
                className="text-nsai-dark font-medium"
              >
                {isRegisterMode ? "Already have an account? Sign in" : "Don't have an account? Register"}
              </Button>
            </div>
          </form>
        </div>
        
        {/* Client logos */}
        <div className="mt-10 hidden md:flex justify-between items-center opacity-60">
          <div className="h-5 w-16 bg-nsai-gray-light rounded"></div>
          <div className="h-5 w-20 bg-nsai-gray-light rounded"></div>
          <div className="h-5 w-18 bg-nsai-gray-light rounded"></div>
          <div className="h-5 w-16 bg-nsai-gray-light rounded"></div>
        </div>
      </div>
      
      {/* Right side - dark background with message */}
      <div className="flex-1 bg-nsai-dark text-white p-6 md:p-10 flex flex-col justify-center items-center text-center animate-fade-in">
        <div className="max-w-xl">
          <div className="w-full h-64 md:h-80 bg-[#12314b] rounded-lg mb-10 flex justify-center items-center animate-float shadow-lg">
            <div className="text-5xl font-bold text-nsai-teal">NS.AI</div>
          </div>
          
          <h2 className="text-3xl md:text-4xl font-bold mb-6 animate-slide-in-right">
            Seize AI opportunities<br />
            for your logistics.
          </h2>
          
          <p className="text-[#a0aec0] leading-relaxed text-base animate-slide-in-left">
            AI-driven process mining for warehouses. Automating repetitive tasks.
            Improving operational excellence with AI technology.
          </p>
          
          <Button
            type="button"
            onClick={() => window.open('https://newsystem-ai.com', '_blank')}
            className="mt-10 px-8 py-3 bg-nsai-teal text-nsai-dark border-none rounded-full text-base font-medium hover:opacity-90 transition-all duration-200 ease-in-out animate-pulse-slow btn-hover"
          >
            Explore NewSystem.AI
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AuthPage; 