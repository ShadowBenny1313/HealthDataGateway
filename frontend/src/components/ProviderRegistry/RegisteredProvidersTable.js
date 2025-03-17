import React, { useState } from 'react';
import {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Button,
  Badge,
  Text,
  Box,
  HStack,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  VStack,
  Heading,
  Alert,
  AlertIcon,
  Flex,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Image,
  Link
} from '@chakra-ui/react';

/**
 * Table component for displaying and managing registered providers
 */
const RegisteredProvidersTable = ({ providers, onUpdateStatus }) => {
  const [selectedProvider, setSelectedProvider] = useState(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  // Handle view details
  const handleViewDetails = (provider) => {
    setSelectedProvider(provider);
    onOpen();
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'inactive':
        return 'red';
      case 'pending':
        return 'yellow';
      case 'suspended':
        return 'orange';
      default:
        return 'gray';
    }
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  // Get the provider type label
  const getProviderTypeLabel = (type) => {
    switch (type) {
      case 'hospital':
        return 'Hospital System';
      case 'pharmacy':
        return 'Pharmacy';
      case 'wearable':
        return 'Wearable/Health Tech';
      case 'lab':
        return 'Laboratory';
      case 'clinic':
        return 'Clinic';
      default:
        return type.charAt(0).toUpperCase() + type.slice(1);
    }
  };

  return (
    <>
      {providers.length === 0 ? (
        <Alert status="info">
          <AlertIcon />
          No registered providers found
        </Alert>
      ) : (
        <Box overflowX="auto">
          <Table variant="simple" size="md">
            <Thead>
              <Tr bg="gray.50">
                <Th>Provider</Th>
                <Th>Type</Th>
                <Th>Registered Date</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {providers.map((provider) => (
                <Tr key={provider.id} _hover={{ bg: 'gray.50' }}>
                  <Td>
                    <Flex align="center">
                      {provider.logo_url && (
                        <Box mr={3} w="30px" h="30px" borderRadius="md" overflow="hidden">
                          <Image src={provider.logo_url} alt={provider.name} fallbackSrc="https://via.placeholder.com/30" />
                        </Box>
                      )}
                      <Text fontWeight="medium">{provider.name}</Text>
                    </Flex>
                  </Td>
                  <Td>
                    <Badge variant="subtle" colorScheme="blue">
                      {getProviderTypeLabel(provider.type)}
                    </Badge>
                  </Td>
                  <Td>{formatDate(provider.registration_date)}</Td>
                  <Td>
                    <Badge colorScheme={getStatusColor(provider.status)}>
                      {provider.status.toUpperCase()}
                    </Badge>
                  </Td>
                  <Td>
                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        variant="outline"
                        onClick={() => handleViewDetails(provider)}
                      >
                        View Details
                      </Button>
                      <Menu>
                        <MenuButton as={Button} size="sm" colorScheme="gray">
                          Status
                        </MenuButton>
                        <MenuList>
                          <MenuItem 
                            onClick={() => onUpdateStatus(provider.id, 'active')}
                            color="green.500"
                          >
                            Set Active
                          </MenuItem>
                          <MenuItem 
                            onClick={() => onUpdateStatus(provider.id, 'inactive')}
                            color="red.500"
                          >
                            Set Inactive
                          </MenuItem>
                          <MenuItem 
                            onClick={() => onUpdateStatus(provider.id, 'suspended')}
                            color="orange.500"
                          >
                            Suspend Provider
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </HStack>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Box>
      )}

      {/* Provider Details Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader borderBottomWidth="1px">
            Provider Details
          </ModalHeader>
          <ModalCloseButton />
          
          <ModalBody py={6}>
            {selectedProvider && (
              <VStack spacing={5} align="stretch">
                <Flex justify="space-between" align="center">
                  <HStack>
                    {selectedProvider.logo_url && (
                      <Box mr={3} w="40px" h="40px" borderRadius="md" overflow="hidden">
                        <Image src={selectedProvider.logo_url} alt={selectedProvider.name} fallbackSrc="https://via.placeholder.com/40" />
                      </Box>
                    )}
                    <Heading as="h3" size="md">{selectedProvider.name}</Heading>
                  </HStack>
                  <Badge colorScheme={getStatusColor(selectedProvider.status)} fontSize="md" px={2} py={1}>
                    {selectedProvider.status.toUpperCase()}
                  </Badge>
                </Flex>
                
                <Box p={4} bg="gray.50" borderRadius="md">
                  <Text fontWeight="bold" mb={1}>Provider Type:</Text>
                  <Text>{getProviderTypeLabel(selectedProvider.type)}</Text>
                  
                  {selectedProvider.description && (
                    <>
                      <Text fontWeight="bold" mt={3} mb={1}>Description:</Text>
                      <Text>{selectedProvider.description}</Text>
                    </>
                  )}
                  
                  {selectedProvider.website && (
                    <>
                      <Text fontWeight="bold" mt={3} mb={1}>Website:</Text>
                      <Link color="blue.500" href={selectedProvider.website} isExternal>
                        {selectedProvider.website}
                      </Link>
                    </>
                  )}
                </Box>
                
                {selectedProvider.contact && (
                  <Box p={4} bg="blue.50" borderRadius="md">
                    <Heading as="h4" size="sm" mb={3}>Contact Information</Heading>
                    
                    {selectedProvider.contact.name && (
                      <Text>
                        <strong>Name:</strong> {selectedProvider.contact.name}
                      </Text>
                    )}
                    
                    {selectedProvider.contact.title && (
                      <Text>
                        <strong>Title:</strong> {selectedProvider.contact.title}
                      </Text>
                    )}
                    
                    {selectedProvider.contact.email && (
                      <Text>
                        <strong>Email:</strong> {selectedProvider.contact.email}
                      </Text>
                    )}
                    
                    {selectedProvider.contact.phone && (
                      <Text>
                        <strong>Phone:</strong> {selectedProvider.contact.phone}
                      </Text>
                    )}
                  </Box>
                )}
                
                {selectedProvider.integration_info && (
                  <Box p={4} bg="green.50" borderRadius="md">
                    <Heading as="h4" size="sm" mb={3}>Integration Details</Heading>
                    
                    {selectedProvider.integration_info.api_documentation && (
                      <Text mb={2}>
                        <strong>API Documentation:</strong>{' '}
                        <Link color="blue.500" href={selectedProvider.integration_info.api_documentation} isExternal>
                          View API Docs
                        </Link>
                      </Text>
                    )}
                    
                    <HStack mt={2} spacing={5}>
                      <Text>
                        <strong>Requires OAuth:</strong>{' '}
                        <Badge colorScheme={selectedProvider.integration_info.requires_oauth ? 'green' : 'gray'}>
                          {selectedProvider.integration_info.requires_oauth ? 'Yes' : 'No'}
                        </Badge>
                      </Text>
                      
                      <Text>
                        <strong>FHIR Support:</strong>{' '}
                        <Badge colorScheme={selectedProvider.integration_info.supports_fhir ? 'green' : 'gray'}>
                          {selectedProvider.integration_info.supports_fhir ? 'Yes' : 'No'}
                        </Badge>
                      </Text>
                    </HStack>
                  </Box>
                )}
                
                {selectedProvider.registration_notes && (
                  <Box p={4} borderRadius="md" borderWidth="1px">
                    <Heading as="h4" size="sm" mb={2}>Registration Notes</Heading>
                    <Text>{selectedProvider.registration_notes}</Text>
                  </Box>
                )}
                
                <Box p={4} bg="gray.100" borderRadius="md">
                  <Text fontSize="sm" color="gray.600">
                    <strong>Registration Date:</strong> {formatDate(selectedProvider.registration_date)}
                  </Text>
                  
                  {selectedProvider.last_updated && (
                    <Text fontSize="sm" color="gray.600">
                      <strong>Last Updated:</strong> {formatDate(selectedProvider.last_updated)}
                    </Text>
                  )}
                </Box>
              </VStack>
            )}
          </ModalBody>

          <ModalFooter borderTopWidth="1px">
            <HStack spacing={3}>
              <Button variant="ghost" onClick={onClose}>
                Close
              </Button>
              {selectedProvider && (
                <Menu>
                  <MenuButton as={Button} colorScheme="blue">
                    Update Status
                  </MenuButton>
                  <MenuList>
                    <MenuItem 
                      onClick={() => {
                        onUpdateStatus(selectedProvider.id, 'active');
                        onClose();
                      }}
                      color="green.500"
                    >
                      Set Active
                    </MenuItem>
                    <MenuItem 
                      onClick={() => {
                        onUpdateStatus(selectedProvider.id, 'inactive');
                        onClose();
                      }}
                      color="red.500"
                    >
                      Set Inactive
                    </MenuItem>
                    <MenuItem 
                      onClick={() => {
                        onUpdateStatus(selectedProvider.id, 'suspended');
                        onClose();
                      }}
                      color="orange.500"
                    >
                      Suspend Provider
                    </MenuItem>
                  </MenuList>
                </Menu>
              )}
            </HStack>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default RegisteredProvidersTable;
